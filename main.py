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
            # Encadenamiento de excepciones
            raise ErrorReserva(f"No se pudo completar la reserva {self.id_res}.") from e
        
        else:
            print(f"-> Reserva {self.id_res} confirmada para {self.cliente.nombre}.")
        
        finally:
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

        # Op 1: Cliente válido
        try:
            print("1. Registrando cliente válido...")
            c1 = Cliente("1098765432", "Carlos Perez", "carlos@mail.com", "3104567890")
            self.clientes.append(c1)
            self.registrar_log("INFO", "Cliente Carlos registrado exitosamente.")
        except Exception as e:
            self.registrar_log("ERROR", f"Error en Op 1: {e}")

        # Op 2: Cliente inválido (cédula con letras)
        try:
            print("2. Intentando registrar cliente con cédula inválida...")
            c2 = Cliente("1098ABC", "Ana", "ana@mail.com", "3201234567")
            self.clientes.append(c2)
        except Exception as e:
            print(f"   [Error controlado]: {e}")
            self.registrar_log("WARNING", f"Validación de cliente fallida: {e}")

        # Op 3: Servicio válido
        try:
            print("3. Creando servicio de reserva de sala...")
            s1 = ReservaSalas("S01", "Sala Ejecutiva", 50000, 10)
            self.servicios.append(s1)
            self.registrar_log("INFO", "Servicio Sala Ejecutiva creado.")
        except Exception as e:
            self.registrar_log("ERROR", f"Error en Op 3: {e}")

        # Op 4: Servicio inválido (costo negativo)
        try:
            print("4. Intentando crear servicio con costo negativo...")
            s_malo = AlquilerEquipos("E00", "Servidor", -100000, "SN123")
            self.servicios.append(s_malo)
        except Exception as e:
            print(f"   [Error controlado]: {e}")
            self.registrar_log("WARNING", f"Validación de servicio fallida: {e}")

        # Op 5: Más servicios válidos
        try:
            print("5. Creando servicios de equipo y asesoría...")
            s2 = AlquilerEquipos("E01", "Escáner", 200000, "RAPI-920")
            s3 = AsesoriaEspecializada("A01", "Auditoría", 150000, "Sistemas")
            self.servicios.extend([s2, s3])
            self.registrar_log("INFO", "Servicios de equipo y asesoría creados.")
        except Exception as e:
            self.registrar_log("ERROR", f"Error en Op 5: {e}")

        # Op 6: Reserva exitosa con descuento (Sobrecarga de parámetros)
        try:
            print("6. Procesando reserva de sala (con descuento)...")
            r1 = Reserva("R001", self.clientes[0], self.servicios[0], 4, descuento=0.1)
            self.reservas.append(r1)
            self.registrar_log("INFO", f"Reserva R001 confirmada. Total: {r1.total}")
        except Exception as e:
            self.registrar_log("ERROR", f"Error en Op 6: {e}")

        # Op 7: Reserva exitosa con seguro (Sobrecarga de parámetros)
        try:
            print("7. Procesando alquiler de equipo (con seguro)...")
            r2 = Reserva("R002", self.clientes[0], self.servicios[1], 3, seguro=True)
            self.reservas.append(r2)
            self.registrar_log("INFO", f"Reserva R002 confirmada. Total: {r2.total}")
        except Exception as e:
            self.registrar_log("ERROR", f"Error en Op 7: {e}")

        # Op 8: Reserva fallida (cantidad negativa)
        try:
            print("8. Intentando reserva con cantidad negativa...")
            r_mala = Reserva("R_ERR", self.clientes[0], self.servicios[0], -2)
            self.reservas.append(r_mala)
        except Exception as e:
            print(f"   [Error controlado]: {e}")
            self.registrar_log("WARNING", f"Reserva fallida controlada: {e}")

        # Op 9: Reserva exitosa de asesoría
        try:
            print("9. Procesando reserva de asesoría...")
            r3 = Reserva("R003", self.clientes[0], self.servicios[2], 2)
            self.reservas.append(r3)
            self.registrar_log("INFO", f"Reserva R003 confirmada. Total: {r3.total}")
        except Exception as e:
            self.registrar_log("ERROR", f"Error en Op 9: {e}")

        # Op 10: Cancelar reserva y probar error de doble cancelación
        try:
            print("10. Cancelando la reserva R001...")
            if self.reservas:
                self.reservas[0].cancelar()
                self.registrar_log("INFO", "Reserva R001 cancelada.")
                
            print("    Intentando cancelar de nuevo (debe fallar)...")
            self.reservas[0].cancelar()
        except Exception as e:
            print(f"   [Error controlado]: {e}")
            self.registrar_log("WARNING", f"Error al cancelar reserva: {e}")

        print("\n=== FIN DE LA SIMULACIÓN ===")
        print(f"Operaciones finalizadas. Revisa el archivo '{self.archivo_log}' para más detalles.")


if __name__ == "__main__":
    app = SistemaSoftwareFJ()
    app.ejecutar_simulacion()