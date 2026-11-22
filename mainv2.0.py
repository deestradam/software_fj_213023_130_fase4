import datetime
from abc import ABC, abstractmethod

# --- Excepciones personalizadas para el sistema ---
class ErrorSoftwareFJ(Exception):
    pass

class ErrorCliente(ErrorSoftwareFJ):
    pass

class ErrorServicio(ErrorSoftwareFJ):
    pass

class ErrorReserva(ErrorSoftwareFJ):
    pass


# --- Clases del sistema ---

class Entidad(ABC):
    """Clase abstracta base para las entidades del sistema."""
    @abstractmethod
    def mostrar_info(self):
        pass


class Cliente(Entidad):
    """Clase Cliente con encapsulamiento y validaciones en los setters."""
    def __init__(self, cedula, nombre, correo, telefono):
        self.cedula = cedula
        self.nombre = nombre
        self.correo = correo
        self.telefono = telefono

    @property
    def cedula(self):
        return self._cedula

    @cedula.setter
    def cedula(self, val):
        if not val or not val.isdigit():
            raise ErrorCliente("La cédula solo debe contener números.")
        self._cedula = val

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, val):
        if not val or len(val.strip()) < 3:
            raise ErrorCliente("El nombre debe tener al menos 3 letras.")
        self._nombre = val

    @property
    def correo(self):
        return self._correo

    @correo.setter
    def correo(self, val):
        if "@" not in val or "." not in val:
            raise ErrorCliente("El formato del correo no es válido.")
        self._correo = val

    @property
    def telefono(self):
        return self._telefono

    @telefono.setter
    def telefono(self, val):
        if not val.isdigit() or len(val) < 7:
            raise ErrorCliente("El teléfono debe tener al menos 7 dígitos numéricos.")
        self._telefono = val

    def mostrar_info(self):
        return f"Cliente: {self.nombre} (CC: {self.cedula})"


class Servicio(ABC):
    """Clase abstracta para los servicios ofrecidos por Software FJ."""
    def __init__(self, id_serv, nombre, costo_base):
        self.id_serv = id_serv
        self.nombre = nombre
        self.costo_base = costo_base

    @property
    def costo_base(self):
        return self._costo_base

    @costo_base.setter
    def costo_base(self, val):
        if val < 0:
            raise ErrorServicio("El costo base no puede ser negativo.")
        self._costo_base = float(val)

    @abstractmethod
    def calcular_costo(self, *args, **kwargs):
        pass

    @abstractmethod
    def descripcion(self):
        pass


class ReservaSalas(Servicio):
    def __init__(self, id_serv, nombre, costo_base, capacidad):
        super().__init__(id_serv, nombre, costo_base)
        self.capacidad = capacidad

    # CORRECCIÓN: Se aclara que 'descuento' es un parámetro opcional, no sobrecarga.
    def calcular_costo(self, horas, descuento=0.0):
        if horas <= 0:
            raise ErrorServicio("Las horas reservadas deben ser mayores a cero.")
        subtotal = self.costo_base * horas
        return subtotal - (subtotal * descuento)

    def descripcion(self):
        return f"Sala: {self.nombre} - Capacidad: {self.capacidad} personas"


class AlquilerEquipos(Servicio):
    def __init__(self, id_serv, nombre, costo_base, serial):
        super().__init__(id_serv, nombre, costo_base)
        self.serial = serial

    # CORRECCIÓN: Se aclara que 'seguro' es un parámetro opcional, no sobrecarga.
    def calcular_costo(self, dias, seguro=False):
        if dias <= 0:
            raise ErrorServicio("Los días de alquiler deben ser mayores a cero.")
        subtotal = self.costo_base * dias
        pago_seguro = 15000 * dias if seguro else 0
        return subtotal + pago_seguro

    def descripcion(self):
        return f"Equipo: {self.nombre} - Serial: {self.serial}"


class AsesoriaEspecializada(Servicio):
    def __init__(self, id_serv, nombre, costo_base, area):
        super().__init__(id_serv, nombre, costo_base)
        self.area = area

    # CORRECCIÓN: Se aclara que 'iva' es un parámetro opcional, no sobrecarga.
    def calcular_costo(self, sesiones, iva=0.19):
        if sesiones <= 0:
            raise ErrorServicio("El número de sesiones debe ser mayor a cero.")
        subtotal = self.costo_base * sesiones
        return subtotal * (1 + iva)

    def descripcion(self):
        return f"Asesoría: {self.nombre} - Área: {self.area}"


class Reserva:
    """Integra al cliente, el servicio y gestiona su estado."""
    def __init__(self, id_res, cliente, servicio, cantidad, *args, **kwargs):
        self.id_res = id_res
        self.cliente = cliente
        self.servicio = servicio
        self.cantidad = cantidad
        self.estado = "Creada"
        self.total = 0.0
        self.procesar_reserva(*args, **kwargs)

    def procesar_reserva(self, *args, **kwargs):
        try:
            if self.cantidad <= 0:
                raise ErrorReserva("La cantidad solicitada no es válida.")
            
            self.total = self.servicio.calcular_costo(self.cantidad, *args, **kwargs)
            self.estado = "Confirmada"
        
        except (ErrorServicio, ValueError) as e:
            self.estado = "Fallida"
            # CORRECCIÓN: Se incluye el mensaje original 'e' en la nueva excepción
            # para que el error sea informativo y no genérico.
            raise ErrorReserva(f"No se pudo completar la reserva {self.id_res}: {e}") from e
        
        else:
            print(f"-> Reserva {self.id_res} confirmada para {self.cliente.nombre}.")
        
        finally:
            # CORRECCIÓN: Se imprime el estado final (útil para depuración)
            print(f"   [Estado final] Reserva {self.id_res}: {self.estado}\n")

    def cancelar(self):
        if self.estado == "Cancelada":
            raise ErrorReserva("Esta reserva ya se encuentra cancelada.")
        self.estado = "Cancelada"
        print(f"-> La reserva {self.id_res} fue cancelada exitosamente.")


class SistemaSoftwareFJ:
    def __init__(self):
        self.archivo_log = "sistema_eventos.log"
        self.clientes = []
        self.servicios = []
        self.reservas = []

    def registrar_log(self, tipo, mensaje):
        """Guarda los eventos en el archivo de texto."""
        hora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.archivo_log, "a", encoding="utf-8") as f:
            f.write(f"[{hora}] [{tipo}] {mensaje}\n")

    def ejecutar_simulacion(self):
        print("=== INICIANDO PRUEBAS DEL SISTEMA SOFTWARE FJ ===\n")
        self.registrar_log("INFO", "=== INICIO DE SIMULACIÓN ===")

        # ============================================================
        # CORRECCIÓN: La simulación ahora consta de 10 OPERACIONES COMPLETAS.
        # Cada operación incluye la creación de cliente, servicio y reserva
        # (válida o inválida), y se registra en el log el resultado completo.
        # ============================================================

        # --- Datos base para las pruebas ---
        # Cliente válido
        try:
            c1 = Cliente("1098765432", "Carlos Perez", "carlos@mail.com", "3104567890")
            self.clientes.append(c1)
            self.registrar_log("INFO", f"Cliente válido creado: {c1.mostrar_info()}")
        except Exception as e:
            self.registrar_log("ERROR", f"Error al crear cliente base: {e}")

        # Servicios válidos
        try:
            s_sala = ReservaSalas("S01", "Sala Ejecutiva", 50000, 10)
            s_equipo = AlquilerEquipos("E01", "Escáner", 200000, "RAPI-920")
            s_asesoria = AsesoriaEspecializada("A01", "Auditoría", 150000, "Sistemas")
            self.servicios.extend([s_sala, s_equipo, s_asesoria])
            self.registrar_log("INFO", "Servicios válidos creados: Sala, Equipo, Asesoría")
        except Exception as e:
            self.registrar_log("ERROR", f"Error al crear servicios base: {e}")

        # ============================================================
        # OPERACIÓN 1: Reserva válida de sala SIN descuento
        # ============================================================
        try:
            print("1. Reserva válida de sala (sin descuento)...")
            r1 = Reserva("R001", self.clientes[0], self.servicios[0], 4)
            self.reservas.append(r1)
            self.registrar_log("INFO", f"Op1: Reserva R001 confirmada. Total: {r1.total}")
        except Exception as e:
            print(f"   [Error controlado]: {e}")
            self.registrar_log("ERROR", f"Op1: Error inesperado: {e}")

        # ============================================================
        # OPERACIÓN 2: Reserva válida de sala CON descuento (parámetro opcional)
        # ============================================================
        try:
            print("2. Reserva válida de sala (con descuento del 10%)...")
            r2 = Reserva("R002", self.clientes[0], self.servicios[0], 5, descuento=0.10)
            self.reservas.append(r2)
            self.registrar_log("INFO", f"Op2: Reserva R002 confirmada. Total: {r2.total}")
        except Exception as e:
            print(f"   [Error controlado]: {e}")
            self.registrar_log("ERROR", f"Op2: Error inesperado: {e}")

        # ============================================================
        # OPERACIÓN 3: Reserva válida de equipo SIN seguro
        # ============================================================
        try:
            print("3. Reserva válida de equipo (sin seguro)...")
            r3 = Reserva("R003", self.clientes[0], self.servicios[1], 3)
            self.reservas.append(r3)
            self.registrar_log("INFO", f"Op3: Reserva R003 confirmada. Total: {r3.total}")
        except Exception as e:
            print(f"   [Error controlado]: {e}")
            self.registrar_log("ERROR", f"Op3: Error inesperado: {e}")

        # ============================================================
        # OPERACIÓN 4: Reserva válida de equipo CON seguro (parámetro opcional)
        # ============================================================
        try:
            print("4. Reserva válida de equipo (con seguro)...")
            r4 = Reserva("R004", self.clientes[0], self.servicios[1], 2, seguro=True)
            self.reservas.append(r4)
            self.registrar_log("INFO", f"Op4: Reserva R004 confirmada. Total: {r4.total}")
        except Exception as e:
            print(f"   [Error controlado]: {e}")
            self.registrar_log("ERROR", f"Op4: Error inesperado: {e}")

        # ============================================================
        # OPERACIÓN 5: Reserva válida de asesoría
        # ============================================================
        try:
            print("5. Reserva válida de asesoría...")
            r5 = Reserva("R005", self.clientes[0], self.servicios[2], 2)
            self.reservas.append(r5)
            self.registrar_log("INFO", f"Op5: Reserva R005 confirmada. Total: {r5.total}")
        except Exception as e:
            print(f"   [Error controlado]: {e}")
            self.registrar_log("ERROR", f"Op5: Error inesperado: {e}")

        # ============================================================
        # OPERACIÓN 6: Reserva INVÁLIDA por cantidad negativa
        # ============================================================
        try:
            print("6. Intento de reserva con cantidad negativa...")
            r6 = Reserva("R006", self.clientes[0], self.servicios[0], -3)
            self.reservas.append(r6)
        except Exception as e:
            print(f"   [Error controlado]: {e}")
            # CORRECCIÓN: Se registra en el log el error completo
            self.registrar_log("WARNING", f"Op6: Reserva inválida controlada: {e}")

        # ============================================================
        # OPERACIÓN 7: Reserva INVÁLIDA por cliente con cédula inválida
        # ============================================================
        try:
            print("7. Intento de crear cliente con cédula inválida y reservar...")
            c_malo = Cliente("1098ABC", "Ana", "ana@mail.com", "3201234567")
            # Si llegara aquí, intentaría reservar
            r7 = Reserva("R007", c_malo, self.servicios[0], 2)
            self.reservas.append(r7)
        except Exception as e:
            print(f"   [Error controlado]: {e}")
            self.registrar_log("WARNING", f"Op7: Cliente inválido controlado: {e}")

        # ============================================================
        # OPERACIÓN 8: Reserva INVÁLIDA por servicio con costo negativo
        # ============================================================
        try:
            print("8. Intento de crear servicio con costo negativo y reservar...")
            s_malo = AlquilerEquipos("E00", "Servidor", -100000, "SN123")
            # Si llegara aquí, intentaría reservar
            r8 = Reserva("R008", self.clientes[0], s_malo, 2)
            self.reservas.append(r8)
        except Exception as e:
            print(f"   [Error controlado]: {e}")
            self.registrar_log("WARNING", f"Op8: Servicio inválido controlado: {e}")

        # ============================================================
        # OPERACIÓN 9: Cancelación válida de una reserva
        # ============================================================
        try:
            print("9. Cancelación de la reserva R001...")
            if self.reservas:
                self.reservas[0].cancelar()
                self.registrar_log("INFO", f"Op9: Reserva {self.reservas[0].id_res} cancelada.")
            else:
                raise ErrorReserva("No hay reservas para cancelar.")
        except Exception as e:
            print(f"   [Error controlado]: {e}")
            self.registrar_log("WARNING", f"Op9: Error al cancelar: {e}")

        # ============================================================
        # OPERACIÓN 10: Intento de doble cancelación (debe fallar)
        # ============================================================
        try:
            print("10. Intento de cancelar de nuevo la reserva R001 (debe fallar)...")
            if self.reservas:
                self.reservas[0].cancelar()
        except Exception as e:
            print(f"   [Error controlado]: {e}")
            self.registrar_log("WARNING", f"Op10: Doble cancelación controlada: {e}")

        # ============================================================
        # FIN DE LA SIMULACIÓN
        # ============================================================
        print("\n=== FIN DE LA SIMULACIÓN ===")
        print(f"Operaciones finalizadas. Revisa el archivo '{self.archivo_log}' para más detalles.")
        self.registrar_log("INFO", "=== FIN DE SIMULACIÓN ===")

        # CORRECCIÓN: Se muestra un resumen de las reservas creadas
        print("\n--- RESUMEN DE RESERVAS ---")
        for r in self.reservas:
            print(f"  {r.id_res}: {r.estado} | Total: {r.total}")
        print("---------------------------")


if __name__ == "__main__":
    app = SistemaSoftwareFJ()
    app.ejecutar_simulacion()