import tkinter as tk
from tkinter import messagebox
import psycopg2
from datetime import datetime ,timedelta


# ---------------------------------------- Conexión a la BD ----------------------------------------
def conectar_bd():
    try:
        conn = psycopg2.connect(
            dbname="postgres",  # Nombre de la base de datos
            user="admin",       # Usuario de la BD
            password="12345",   # Contraseña de la BD
            host="localhost",   # Host local
            port="5555"         # Puerto de PostgreSQL
        )
        return conn
    except Exception as e:
        messagebox.showerror("Error", f"Error de conexión a la base de datos: {e}")
        return None

# ---------------------------------------- Inicio de Sesión ----------------------------------------
def iniciar_sesion():
    username = entry_username.get()
    contrasena = entry_contrasena.get()

    conn = conectar_bd()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE username = %s AND password = %s", (username, contrasena))
        user = cursor.fetchone()

        if user:
            rol = user[3]  # Suponiendo que el rol está en la columna 4
            if rol in (1, 2):  # Solo trabajadores y gerentes
                messagebox.showinfo("Éxito", f"Bienvenido {user[3]}! (Rol: {'Trabajador' if rol == 1 else 'Gerente'})")
                ventana_principal.withdraw()  # Ocultar ventana de inicio de sesión
                mostrar_dashboard_trabajador()  # Mostrar el dashboard del trabajador
            else:
                messagebox.showinfo("Acceso denegado", "Este usuario no tiene permisos para acceder.")
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos.")
        
        cursor.close()
        conn.close()

# ---------------------------------------- Función para cerrar el dashboard ----------------------------------------
def cerrar_dashboard_trabajador(ventana_dashboard):
    ventana_dashboard.destroy()
    ventana_principal.deiconify()  # Volver a mostrar la ventana principal

def cerrar_ventana(ventana):
    ventana.destroy()


# ---------------------------------------- Función para mostrar el dashboard del trabajador ----------------------------------------
import tkinter as tk
from tkinter import messagebox, simpledialog

# Inicializar variables globales
total_pedido = 0.0
subtotal_pedido = 0.0
ticket_text = None
subtotal_label = None
total_label = None

def mostrar_dashboard_trabajador():
    ventana_dashboard = tk.Toplevel()
    ventana_dashboard.title("Dashboard del Trabajador")
    ventana_dashboard.geometry("1500x900")  # Ajustar el tamaño de la ventana

    ventana_dashboard.protocol("WM_DELETE_WINDOW", lambda: cerrar_dashboard_trabajador(ventana_dashboard))

    # Título de bienvenida
    tk.Label(ventana_dashboard, text="Bienvenido a Farmacias Leo", font=("Helvetica", 16), bg="lightblue").pack(side=tk.TOP, fill=tk.X, pady=10)

    # Crear el frame para los botones y organizarlos en una cuadrícula
    botones_frame = tk.Frame(ventana_dashboard, bg="lightgray", width=300, height=600)
    botones_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

    # Definir colores y textos para los botones
    botones = [
        ("Pedido a proveedores", "red"),
        ("Inventario", "orange"),
        ("Medicamentos", "purple"),
        ("Alimentos", "lightgreen"),
        ("Higiene", "cyan"),
        ("Proveedores", "red"),
        ("Historial de compras", "pink"),
        ("Registrar Producto", "gray"),
        ("Manejo de Compras", "orange"),
    ]

    # Crear los botones y organizarlos en una cuadrícula 2x4
    for i, (texto, color) in enumerate(botones):
        fila = i // 2  # Dividir los botones en filas
        columna = i % 2  # Dividir en dos columnas
        boton = tk.Button(botones_frame, text=texto, bg=color, width=20, height=10)
        boton.grid(row=fila, column=columna, padx=1, pady=5)
        
        # Asignar las funciones correspondientes a los botones
        if texto == "Proveedores":
            boton.config(command=mostrar_registro_proveedor)
        elif texto == "Registrar Producto":
            boton.config(command=mostrar_registro_producto)
        elif texto == "Inventario":
            boton.config(command=mostrar_inventario)
        elif texto == "Alimentos":
            boton.config(command=mostrar_inventario_alimentos)
        elif texto == "Medicamentos":
            boton.config(command=mostrar_inventario_medicamentos)
        elif texto == "Higiene":
            boton.config(command=mostrar_inventario_higiene)
        elif texto == "Pedido a proveedores":
            boton.config(command=mostrar_pedido_proveedor)
        elif texto == "Manejo de Compras":
            boton.config(command=lambda: mostrar_manejo_compra(contenido_frame))    
        elif texto == "Historial de compras":
            boton.config(command=mostrar_historial_pedidos)

    # Crear la barra de búsqueda y el área de contenido
    buscar_frame = tk.Frame(ventana_dashboard)
    buscar_frame.pack(side=tk.TOP, pady=20)

    buscar_inner_frame = tk.Frame(buscar_frame)
    buscar_inner_frame.pack()  # Este frame interno centrará los elementos de búsqueda

    entry_codigo_barras = tk.Entry(buscar_inner_frame, width=30)
    entry_codigo_barras.pack(side=tk.LEFT, padx=5)
    
    tk.Button(buscar_inner_frame, text="Buscar", command=lambda: buscar_producto(entry_codigo_barras.get())).pack(side=tk.LEFT)

    contenido_frame = tk.Frame(ventana_dashboard, bg="orange", width=500, height=300)
    contenido_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Convertir el área del manejo de compras en un botón
    manejo_compra_label = tk.Label(contenido_frame, text="Módulo del Manejo de Compras", bg="orange", font=("Helvetica", 14))
    manejo_compra_label.pack(expand=True)

    manejo_compra_label.bind("<Button-1>", lambda event: mostrar_manejo_compra(contenido_frame))

    def buscar_producto(codigo_barras):
        """Busca el producto en la base de datos por el código de barras"""
        producto, precio = obtener_producto_por_codigo(codigo_barras)  # Buscar el producto en la base de datos

        if producto:
            # Si se encuentra el producto, mostrar su nombre y precio
            messagebox.showinfo("Producto Encontrado", f"Producto: {producto}\nPrecio: ${precio:.2f}")
        else:
            # Si no se encuentra el producto, preguntar si desea registrarlo
            respuesta = messagebox.askyesno("Producto No Encontrado", "El producto no está registrado. ¿Desea registrar un nuevo producto?")
            if respuesta:
                mostrar_registro_producto()  # Llamar a la función para registrar un nuevo producto

# Función que obtiene el producto por código de barras
def obtener_producto_por_codigo(codigo_barras):
    """Busca el producto en la base de datos por código de barras y devuelve su nombre y precio."""
    conn = conectar_bd()  # Conectar a la base de datos
    producto = None
    precio = 0.0
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT nombre_producto, precio_unitario FROM productos WHERE codigo_barras = %s", (codigo_barras,))
        resultado = cursor.fetchone()
        if resultado:
            producto, precio = resultado
        cursor.close()
        conn.close()
    return producto, precio




# Función para buscar producto por código de barras
def buscar_producto_por_codigo(codigo_barras):
    conn = conectar_bd()
    if not conn:
        return None
    cursor = conn.cursor()
    cursor.execute("SELECT nombre_producto, precio_unitario, id FROM productos WHERE codigo_barras = %s", (codigo_barras,))
    producto = cursor.fetchone()
    cursor.close()
    conn.close()
    return producto

# Función para actualizar el stock
def actualizar_stock(codigo_barras):
    conn = conectar_bd()
    if not conn:
        return
    cursor = conn.cursor()
    cursor.execute("UPDATE productos SET stock = stock - 1 WHERE codigo_barras = %s", (codigo_barras,))
    conn.commit()
    cursor.close()
    conn.close()

# Función para mostrar manejo de compra
def mostrar_manejo_compra(frame):
    for widget in frame.winfo_children():
        widget.destroy()

    entry_codigo = tk.Entry(frame, width=30)
    entry_codigo.pack(pady=5)
    entry_codigo.bind('<Return>', lambda event: agregar_producto(entry_codigo.get(), ticket_text, subtotal_label, total_label, entry_codigo))

    ticket_frame = tk.Frame(frame, bg="lightyellow")
    ticket_frame.pack(fill=tk.BOTH, expand=True, pady=10)

    tk.Label(ticket_frame, text="Ticket de Compra", bg="lightyellow", font=("Helvetica", 12)).pack()

    global ticket_text
    ticket_text = tk.Text(ticket_frame, height=10, width=40)
    ticket_text.pack(pady=5)

    global subtotal_label
    subtotal_label = tk.Label(frame, text="Subtotal: $0.00", bg="orange", font=("Helvetica", 12))
    subtotal_label.pack(pady=5)

    global total_label
    total_label = tk.Label(frame, text="Total: $0.00", bg="orange", font=("Helvetica", 12))
    total_label.pack(pady=5)

    tk.Button(frame, text="Pagar", bg="green", command=realizar_pago).pack(pady=10)

    global total_pedido
    total_pedido = 0
    global subtotal_pedido
    subtotal_pedido = 0
    global ids_productos  # Para almacenar IDs de productos
    ids_productos = []  # Lista para almacenar los IDs de productos
    global cantidades  # Para almacenar cantidades de productos
    cantidades = []  # Lista para almacenar las cantidades de productos

# Función para agregar producto al ticket
def agregar_producto(codigo_barras, ticket_text, subtotal_label, total_label, entry_codigo):
    global subtotal_pedido  # Se declara como global
    global total_pedido  # Se declara como global
    global ids_productos  # Acceso a la lista de IDs de productos
    global cantidades  # Acceso a la lista de cantidades

    producto = buscar_producto_por_codigo(codigo_barras)

    if producto:
        nombre, precio, id_producto = producto  # Ahora también obtenemos el ID del producto
        precio = float(precio)

        # Mostrar el producto en el ticket
        ticket_text.insert(tk.END, f"{nombre} - ${precio:.2f}\n")

        # Sumar al subtotal y al total
        subtotal_pedido += precio
        total_pedido = subtotal_pedido  # Aquí puedes agregar impuestos si es necesario

        # Actualizar las etiquetas de subtotal y total
        subtotal_label.config(text=f"Subtotal: ${subtotal_pedido:.2f}")
        total_label.config(text=f"Total: ${total_pedido:.2f}")

        # Limpiar el campo de entrada después de agregar el producto
        entry_codigo.delete(0, tk.END)

        # Actualizar stock en la base de datos
        actualizar_stock(codigo_barras)

        # Acumular el ID del producto
        if id_producto in ids_productos:
            index = ids_productos.index(id_producto)
            cantidades[index] += 1  # Incrementar cantidad si el producto ya está en la lista
        else:
            ids_productos.append(id_producto)
            cantidades.append(1)  # Iniciar la cantidad para este producto
        
    else:
        messagebox.showerror("Error", "Producto no encontrado")
        entry_codigo.delete(0, tk.END)

# Función para obtener puntos acumulados
def obtener_puntos_acumulados(codigo_cupon):
    puntos = 0
    with conectar_bd() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT puntos_acumulados FROM cupones WHERE codigo_cupon = %s", (codigo_cupon,))
            result = cursor.fetchone()
            if result:
                puntos = result[0]  # Obtener los puntos acumulados
            else:
                messagebox.showwarning("Cupón inválido", "El código de cupón ingresado no es válido.")
    return puntos

# Función para manejar el pago
def realizar_pago():
    global total_pedido  # Se declara como global aquí también
    global ids_productos  # Se declara como global
    global cantidades  # Se declara como global

    if total_pedido == 0:
        messagebox.showwarning("Advertencia", "No hay productos en el ticket.")
        return

    # Pedir el código del cupón/membresía
    codigo_cupon = simpledialog.askstring("Membresía", "Ingrese su código de membresía")

    if not codigo_cupon:
        messagebox.showwarning("Advertencia", "Debe ingresar un código de membresía.")
        return

    # Verificar puntos acumulados del cliente
    puntos_acumulados = obtener_puntos_acumulados(codigo_cupon)  # Función para obtener los puntos actuales del cliente

    # Aplicar el descuento si tiene 5 o más puntos
    if puntos_acumulados >= 10:
        descuento = total_pedido * 0.50  # Aplicar el 50% de descuento
        total_pedido -= descuento  # Aplicar el descuento al total
        messagebox.showinfo("Descuento Aplicado", "Se ha aplicado un 50% de descuento por puntos acumulados.")
        # Restar los 5 puntos por usar el descuento
        actualizar_puntos_cliente(codigo_cupon, -10)  # Restar puntos después de aplicar el descuento

    # Aquí continúa, se muestre o no el descuento
    # Mostrar el total actualizado antes de pedir el monto de pago
    messagebox.showinfo("Total a Pagar", f"El total a pagar es: ${total_pedido:.2f}")

    # Pedir el monto con el que se paga
    monto_pago = simpledialog.askfloat("Pago", f"Ingrese el monto con el que se pagó. Total a pagar: ${total_pedido:.2f}")
    
    if monto_pago is None:
        return  # Cancelar si el usuario cierra el cuadro de diálogo

    if monto_pago < total_pedido:
        messagebox.showerror("Error", "El monto pagado es menor que el total.")
        return

    # Calcular cambio
    cambio = monto_pago - total_pedido
    messagebox.showinfo("Pago realizado", f"Pago recibido: ${monto_pago:.2f}\nCambio: ${cambio:.2f}")

    # Guardar la compra en la base de datos
    guardar_compra(monto_pago, cambio, ids_productos, cantidades)

    # Determinar la cantidad de puntos que se sumarán en función del total de la compra
    puntos_a_sumar = 0
    if total_pedido >= 100 and total_pedido < 200:
        puntos_a_sumar = 1
    elif total_pedido >= 200 and total_pedido < 500:
        puntos_a_sumar = 2
    elif total_pedido >= 500:
        puntos_a_sumar = 3

    if puntos_a_sumar > 0:
        actualizar_puntos_cliente(codigo_cupon, puntos_a_sumar)  # Sumar los puntos correspondientes

    # Reiniciar el ticket
    global subtotal_pedido
    subtotal_pedido = 0.0
    total_pedido = 0.0
    ids_productos = []  # Reiniciar lista de IDs
    cantidades = []  # Reiniciar lista de cantidades
    ticket_text.delete(1.0, tk.END)
    subtotal_label.config(text="Subtotal: $0.00")
    total_label.config(text="Total: $0.00")

def actualizar_puntos_cliente(codigo_cupon, puntos):
    """
    Actualiza los puntos del cliente basado en su código de cupón/membresía.
    Se puede sumar o restar puntos.
    """
    try:
        # Conexión a la base de datos
        conn = conectar_bd()
        cursor = conn.cursor()

        # Consulta para obtener los puntos actuales del cliente
        cursor.execute("SELECT puntos_acumulados FROM cupones WHERE codigo_cupon = %s", (codigo_cupon,))
        resultado = cursor.fetchone()

        if resultado is None:
            messagebox.showerror("Error", "Código de membresía no encontrado.")
            return

        puntos_actuales = resultado[0]

        # Calcular los nuevos puntos
        nuevos_puntos = puntos_actuales + puntos

        # Asegurarse de que los puntos no sean negativos
        if nuevos_puntos < 0:
            nuevos_puntos = 0

        # Actualizar los puntos del cliente en la base de datos
        cursor.execute("UPDATE cupones SET puntos_acumulados = %s WHERE codigo_cupon = %s", (nuevos_puntos, codigo_cupon))

        # Confirmar los cambios
        conn.commit()

        #messagebox.showinfo("Actualización Exitosa", f"Los puntos del cliente han sido actualizados a {nuevos_puntos}.")

    except Exception as e:
        messagebox.showerror("Error de Base de Datos", f"Ha ocurrido un error al actualizar los puntos: {str(e)}")
    
    finally:
        # Cerrar la conexión a la base de datos
        cursor.close()
        conn.close()

# Función para guardar la compra en la base de datos
def guardar_compra(pagado, cambio, ids_productos, cantidades):
    conn = conectar_bd()
    if not conn:
        return

    cursor = conn.cursor()

    # Convertir listas a formato string
    ids_productos_str = ','.join(map(str, ids_productos))
    cantidades_str = ','.join(map(str, cantidades))
    
    # Suponiendo que hay un campo en la tabla de compras para el precio unitario, total, fecha, etc.
    total_compra = subtotal_pedido  # Total a pagar es el subtotal
    precio_unitario = total_compra / sum(cantidades) if cantidades else 0

    cursor.execute("""
        INSERT INTO compras (precio_unitario, total, fecha, pagado, cambio, ids_productos, cantidad)
        VALUES (%s, %s, CURRENT_TIMESTAMP, %s, %s, %s, %s)
    """, (precio_unitario, total_compra, pagado, cambio, ids_productos_str, cantidades_str))
    
    conn.commit()
    cursor.close()
    conn.close()

# Configuración de la ventana principal


def mostrar_registro_producto():
    """Función que abre la ventana para registrar un nuevo producto."""
    ventana_registro = tk.Toplevel()
    ventana_registro.title("Registrar Nuevo Producto")
    ventana_registro.geometry("400x300")

    tk.Label(ventana_registro, text="Nombre del Producto:").pack(pady=10)
    entry_nombre_producto = tk.Entry(ventana_registro)
    entry_nombre_producto.pack(pady=10)

    tk.Label(ventana_registro, text="Código de Barras:").pack(pady=10)
    entry_codigo_barras = tk.Entry(ventana_registro)
    entry_codigo_barras.pack(pady=10)

    tk.Label(ventana_registro, text="Precio Unitario:").pack(pady=10)
    entry_precio = tk.Entry(ventana_registro)
    entry_precio.pack(pady=10)

    def guardar_producto():
        nombre_producto = entry_nombre_producto.get()
        codigo_barras = entry_codigo_barras.get()
        precio = entry_precio.get()

        if not nombre_producto or not codigo_barras or not precio:
            messagebox.showerror("Error", "Todos los campos son obligatorios.")
            return

        try:
            precio_float = float(precio)
            if precio_float < 0:
                messagebox.showerror("Error", "El precio no puede ser negativo.")
                return
        except ValueError:
            messagebox.showerror("Error", "El precio debe ser un número válido.")
            return

        conn = conectar_bd()
        if conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO productos (nombre_producto, codigo_barras, precio_unitario) VALUES (%s, %s, %s)",
                (nombre_producto, codigo_barras, precio_float)
            )
            conn.commit()
            cursor.close()
            conn.close()
            messagebox.showinfo("Éxito", "Producto registrado exitosamente.")
            ventana_registro.destroy()
        else:
            messagebox.showerror("Error", "No se pudo conectar a la base de datos.")

    tk.Button(ventana_registro, text="Guardar Producto", command=guardar_producto).pack(pady=10)


# ---------------------------------------- Función para mostrar la ventana de registro de proveedores ----------------------------------------
def mostrar_registro_proveedor():
    ventana_registro = tk.Toplevel()
    ventana_registro.title("Registro de Proveedores")
    ventana_registro.geometry("500x500") 

    tk.Label(ventana_registro, text="Nombre del proveedor:").pack(pady=5)
    entry_nombre = tk.Entry(ventana_registro)
    entry_nombre.pack(pady=5)

    tk.Label(ventana_registro, text="Teléfono:").pack(pady=5)
    entry_telefono = tk.Entry(ventana_registro)
    entry_telefono.pack(pady=5)

    tk.Label(ventana_registro, text="Correo electrónico:").pack(pady=5)
    entry_email = tk.Entry(ventana_registro)
    entry_email.pack(pady=5)

    tk.Button(ventana_registro, text="Registrar Proveedor", command=lambda: registrar_proveedor(entry_nombre.get(), entry_telefono.get(), entry_email.get(), ventana_registro)).pack(pady=20)


# ---------------------------------------- Función para registrar proveedor ----------------------------------------
def registrar_proveedor(nombre, telefono, email,ventana):
    if not nombre or not telefono or not email:
        messagebox.showwarning("Advertencia", "Todos los campos son obligatorios.")
        return

    conn = conectar_bd()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO proveedores (nombre, telefono, email) VALUES (%s, %s, %s)",
                (nombre, telefono, email)
            )
            conn.commit()
            messagebox.showinfo("Éxito", "Proveedor registrado exitosamente.")
            cerrar_ventana(ventana)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo registrar el proveedor: {e}")
        finally:
            cursor.close()
            conn.close()
# ---------------------------------------- Función para mostrar la ventana de registro de productos ----------------------------------------

# ---------------------------------------- Función para obtener proveedores registrados ----------------------------------------
def obtener_proveedores():
    conn = conectar_bd()
    proveedores = []
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT nombre FROM proveedores")  # Asumiendo que tienes una tabla de proveedores
        proveedores = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
    return proveedores

# ---------------------------------------- Función para registrar producto ----------------------------------------

def mostrar_registro_producto():
    ventana_registro_producto = tk.Toplevel()
    ventana_registro_producto.title("Registro de Productos")
    ventana_registro_producto.geometry("400x600")

    tk.Label(ventana_registro_producto, text="Descripción del Producto:").pack(pady=5)
    entry_descripcion = tk.Entry(ventana_registro_producto)
    entry_descripcion.pack(pady=5)

    tk.Label(ventana_registro_producto, text="Código de Barras:").pack(pady=5)
    entry_codigo_barras = tk.Entry(ventana_registro_producto)
    entry_codigo_barras.pack(pady=5)

    fecha_actual = datetime.now().strftime("%d/%m/%Y")
    entry_fecha = tk.Entry(ventana_registro_producto)
    entry_fecha.insert(0, fecha_actual)  # Insertar la fecha en el campo
    entry_fecha.pack(pady=5)

    tk.Label(ventana_registro_producto, text="Proveedor:").pack(pady=5)
    proveedores = obtener_proveedores()  # Función que debes implementar
    entry_proveedor = tk.StringVar()
    combo_proveedor = tk.OptionMenu(ventana_registro_producto, entry_proveedor, *proveedores)
    combo_proveedor.pack(pady=5)

    tk.Label(ventana_registro_producto, text="Área:").pack(pady=5)
    areas = obtener_areas()  # Función que debes implementar para obtener las áreas
    entry_area = tk.StringVar()
    combo_area = tk.OptionMenu(ventana_registro_producto, entry_area, *areas)
    combo_area.pack(pady=5)

    tk.Label(ventana_registro_producto, text="Cantidad:").pack(pady=5)
    entry_cantidad = tk.Entry(ventana_registro_producto)
    entry_cantidad.pack(pady=5)

    tk.Label(ventana_registro_producto, text="Precio Unitario:").pack(pady=5)
    entry_precio_unitario = tk.Entry(ventana_registro_producto)
    entry_precio_unitario.pack(pady=5)

    # Asegúrate de pasar correctamente el objeto ventana_registro_producto
    tk.Button(ventana_registro_producto, text="Registrar Producto", 
              command=lambda: registrar_producto(
                  entry_descripcion.get(), 
                  entry_codigo_barras.get(), 
                  entry_area.get(), 
                  entry_proveedor.get(), 
                  entry_cantidad.get(),
                  entry_precio_unitario.get(),
                  ventana_registro_producto)).pack(pady=20)

def registrar_producto(descripcion, codigo_barras, id_area, proveedor, cantidad, precio_unitario, ventana):
    if not descripcion or not codigo_barras or not id_area or not proveedor or not cantidad or not precio_unitario:
        messagebox.showwarning("Advertencia", "Todos los campos son obligatorios.")
        return

    # Verificar si el código de barras ya existe
    if codigo_barras_existe(codigo_barras):
        messagebox.showwarning("Advertencia", "El código de barras ya está registrado.")
        return

    # Obtener la fecha actual
    fecha_registro = datetime.now().strftime("%Y-%m-%d")  # Formato: AAAA-MM-DD

    conn = conectar_bd()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO productos (nombre_producto, codigo_barras, fecha_registro, area, proveedor, stock, precio_unitario) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (descripcion, codigo_barras, fecha_registro, id_area, proveedor, cantidad, precio_unitario)
            )
            conn.commit()
            messagebox.showinfo("Éxito", "Producto registrado exitosamente.")
            cerrar_ventana(ventana)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo registrar el producto: {e}")
        finally:
            cursor.close()
            conn.close()
def codigo_barras_existe(codigo_barras):
    conn = conectar_bd()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM productos WHERE codigo_barras = %s", (codigo_barras,))
        existe = cursor.fetchone()[0] > 0
        cursor.close()
        conn.close()
        return existe
    return False


# ---------------------------------------- Función para obtener áreas registradas ----------------------------------------
def obtener_areas():
    conn = conectar_bd()
    areas = []
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT nombre_area FROM areas")  # Asegúrate de que el nombre de columna sea correcto
        areas = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
    print("Áreas obtenidas:", areas)  # Mensaje de depuración
    return areas

# ---------------------------------------- Función para obtener productos registrados ----------------------------------------
def obtener_productos():
    conn = conectar_bd()
    productos = []
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT nombre_producto, proveedor, stock, precio_unitario, codigo_barras FROM productos")  # Asegúrate de que los nombres de columna sean correctos
        productos = cursor.fetchall()  # Obtener todos los registros
        cursor.close()
        conn.close()
    return productos
def mostrar_inventario():
    productos = obtener_productos()  # Obtener productos de la base de datos

    # Verifica si hay productos para mostrar
    if not productos:
        messagebox.showinfo("Inventario", "No hay productos registrados.")
        return

    ventana_inventario = tk.Toplevel()
    ventana_inventario.title("Inventario de Productos")
    ventana_inventario.geometry("600x400")

    # Crear tabla de productos
    tabla = tk.Frame(ventana_inventario)
    tabla.pack(pady=10)

    # Encabezados
    tk.Label(tabla, text="Nombre", font=("Helvetica", 12)).grid(row=0, column=0, padx=10, pady=10)
    tk.Label(tabla, text="Proveedor", font=("Helvetica", 12)).grid(row=0, column=1, padx=10, pady=10)
    tk.Label(tabla, text="Stock", font=("Helvetica", 12)).grid(row=0, column=2, padx=10, pady=10)
    tk.Label(tabla, text="Precio Unitario", font=("Helvetica", 12)).grid(row=0, column=3, padx=10, pady=10)
    tk.Label(tabla, text="Codigo de Barras", font=("Helvetica", 12)).grid(row=0, column=4, padx=10, pady=10)

    # Rellenar la tabla con productos
    for i, producto in enumerate(productos):
        for j, valor in enumerate(producto):
            tk.Label(tabla, text=valor).grid(row=i + 1, column=j, padx=10, pady=5)
# Función para obtener productos con filtro por código de barras
def obtener_productos(nombre_filtro="", proveedor_filtro="", stock_filtro="", codigo_barras_filtro=""):
    conn = conectar_bd()
    productos = []
    if conn:
        cursor = conn.cursor()

        # Construir la consulta con los filtros aplicados si se proporcionan
        query = "SELECT nombre_producto, proveedor, stock, precio_unitario, codigo_barras FROM productos WHERE 1=1"
        if nombre_filtro:
            query += " AND nombre_producto ILIKE %s"
        if proveedor_filtro:
            query += " AND proveedor ILIKE %s"
        if stock_filtro:
            query += " AND stock = %s"
        if codigo_barras_filtro:
            query += " AND codigo_barras = %s"

        # Crear una lista de parámetros a pasar en la consulta
        parametros = []
        if nombre_filtro:
            parametros.append(f"%{nombre_filtro}%")
        if proveedor_filtro:
            parametros.append(f"%{proveedor_filtro}%")
        if stock_filtro:
            parametros.append(stock_filtro)
        if codigo_barras_filtro:
            parametros.append(codigo_barras_filtro)

        # Log para verificar la consulta SQL
        print("Consulta SQL:", query)
        print("Parámetros:", parametros)

        cursor.execute(query, parametros)
        productos = cursor.fetchall()  # Obtener todos los registros

        # Log para verificar los productos obtenidos
        print("Productos obtenidos:", productos)

        cursor.close()
        conn.close()
    return productos

# Función para mostrar el inventario con filtros, incluyendo código de barras
def mostrar_inventario():
    ventana_inventario = tk.Toplevel()
    ventana_inventario.title("Inventario de Productos")
    ventana_inventario.geometry("800x500")

    # Crear un frame para los filtros
    filtro_frame = tk.Frame(ventana_inventario)
    filtro_frame.pack(pady=10)

    # Campos de búsqueda para los filtros
    tk.Label(filtro_frame, text="Nombre:").grid(row=0, column=0, padx=10)
    nombre_entry = tk.Entry(filtro_frame)
    nombre_entry.grid(row=0, column=1, padx=10)

    tk.Label(filtro_frame, text="Proveedor:").grid(row=0, column=2, padx=10)
    proveedor_entry = tk.Entry(filtro_frame)
    proveedor_entry.grid(row=0, column=3, padx=10)

    tk.Label(filtro_frame, text="Stock:").grid(row=0, column=4, padx=10)
    stock_entry = tk.Entry(filtro_frame)
    stock_entry.grid(row=0, column=5, padx=10)

    tk.Label(filtro_frame, text="Código de Barras:").grid(row=0, column=6, padx=10)
    codigo_barras_entry = tk.Entry(filtro_frame)
    codigo_barras_entry.grid(row=0, column=7, padx=10)

    # Crear tabla de productos
    tabla_frame = tk.Frame(ventana_inventario)
    tabla_frame.pack(pady=10)

    # Encabezados de la tabla
    tk.Label(tabla_frame, text="Nombre", font=("Helvetica", 12)).grid(row=0, column=0, padx=10, pady=10)
    tk.Label(tabla_frame, text="Proveedor", font=("Helvetica", 12)).grid(row=0, column=1, padx=10, pady=10)
    tk.Label(tabla_frame, text="Stock", font=("Helvetica", 12)).grid(row=0, column=2, padx=10, pady=10)
    tk.Label(tabla_frame, text="Precio Unitario", font=("Helvetica", 12)).grid(row=0, column=3, padx=10, pady=10)
    tk.Label(tabla_frame, text="Código de Barras", font=("Helvetica", 12)).grid(row=0, column=4, padx=10, pady=10)

    # Función para actualizar la tabla según los filtros
    def actualizar_tabla():
        # Obtener valores de los filtros
        nombre_filtro = nombre_entry.get()
        proveedor_filtro = proveedor_entry.get()
        stock_filtro = stock_entry.get()
        codigo_barras_filtro = codigo_barras_entry.get()

        # Log para verificar los valores de los filtros
        print("Nombre filtro:", nombre_filtro)
        print("Proveedor filtro:", proveedor_filtro)
        print("Stock filtro:", stock_filtro)
        print("Código de Barras filtro:", codigo_barras_filtro)

        # Obtener productos filtrados
        productos = obtener_productos(nombre_filtro, proveedor_filtro, stock_filtro, codigo_barras_filtro)

        # Limpiar la tabla antes de llenarla con los nuevos productos
        for widget in tabla_frame.winfo_children():
            widget.destroy()

        # Volver a colocar los encabezados
        tk.Label(tabla_frame, text="Nombre", font=("Helvetica", 12)).grid(row=0, column=0, padx=10, pady=10)
        tk.Label(tabla_frame, text="Proveedor", font=("Helvetica", 12)).grid(row=0, column=1, padx=10, pady=10)
        tk.Label(tabla_frame, text="Stock", font=("Helvetica", 12)).grid(row=0, column=2, padx=10, pady=10)
        tk.Label(tabla_frame, text="Precio Unitario", font=("Helvetica", 12)).grid(row=0, column=3, padx=10, pady=10)
        tk.Label(tabla_frame, text="Código de Barras", font=("Helvetica", 12)).grid(row=0, column=4, padx=10, pady=10)

        # Rellenar la tabla con los productos filtrados
        for i, producto in enumerate(productos):
            for j, valor in enumerate(producto):
                tk.Label(tabla_frame, text=valor).grid(row=i+1, column=j, padx=10, pady=5)

    # Botón para aplicar filtros
    boton_filtro = tk.Button(filtro_frame, text="Buscar", command=actualizar_tabla)
    boton_filtro.grid(row=0, column=8, padx=10)

    # Mostrar todo el inventario al abrir la ventana por primera vez
    actualizar_tabla()

# ---------------------------------------- Función para obtener productos por categoría "Alimentos" ----------------------------------------
def obtener_productos_alimentos(filtros=None):
    conn = conectar_bd()
    productos = []
    query = "SELECT nombre_producto, proveedor, stock, precio_unitario, codigo_barras FROM productos WHERE area = 'Alimentos'"
    
    condiciones = []
    parametros = []
    
    if filtros:
        if filtros.get('nombre'):
            condiciones.append("nombre_producto ILIKE %s")
            parametros.append(f"%{filtros['nombre']}%")
        if filtros.get('proveedor'):
            condiciones.append("proveedor ILIKE %s")
            parametros.append(f"%{filtros['proveedor']}%")
        if filtros.get('stock'):
            condiciones.append("stock = %s")
            parametros.append(filtros['stock'])
        if filtros.get('codigo_barras'):
            condiciones.append("codigo_barras = %s")
            parametros.append(filtros['codigo_barras'])

    if condiciones:
        query += " AND " + " AND ".join(condiciones)

    if conn:
        cursor = conn.cursor()
        cursor.execute(query, parametros)
        productos = cursor.fetchall()
        cursor.close()
        conn.close()

    return productos

# ---------------------------------------- Función para mostrar inventario de Alimentos ----------------------------------------
def mostrar_inventario_alimentos():
    ventana_alimentos = tk.Toplevel()
    ventana_alimentos.title("Inventario de Alimentos")
    ventana_alimentos.geometry("700x500")
    
    # Frame para filtros

    filtros_frame = tk.Frame(ventana_alimentos)
    filtros_frame.pack(pady=10)
    
    # Campos de entrada para los filtros
    tk.Label(filtros_frame, text="Nombre:").grid(row=0, column=0, padx=5, pady=5)
    entrada_nombre = tk.Entry(filtros_frame)
    entrada_nombre.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(filtros_frame, text="Proveedor:").grid(row=0, column=2, padx=5, pady=5)
    entrada_proveedor = tk.Entry(filtros_frame)
    entrada_proveedor.grid(row=0, column=3, padx=5, pady=5)

    tk.Label(filtros_frame, text="Stock:").grid(row=1, column=0, padx=5, pady=5)
    entrada_stock = tk.Entry(filtros_frame)
    entrada_stock.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(filtros_frame, text="Código de Barras:").grid(row=1, column=2, padx=5, pady=5)
    entrada_codigo_barras = tk.Entry(filtros_frame)
    entrada_codigo_barras.grid(row=1, column=3, padx=5, pady=5)

    # Botón para aplicar filtros
    def aplicar_filtros():
        filtros = {
            'nombre': entrada_nombre.get(),
            'proveedor': entrada_proveedor.get(),
            'stock': entrada_stock.get(),
            'codigo_barras': entrada_codigo_barras.get(),
        }
        productos = obtener_productos_alimentos(filtros)
        mostrar_productos(tabla, productos)

    boton_filtrar = tk.Button(filtros_frame, text="Buscar", command=aplicar_filtros)
    boton_filtrar.grid(row=2, column=0, columnspan=4, pady=10)

    # Frame para mostrar los productos
    tabla = tk.Frame(ventana_alimentos)
    tabla.pack(pady=10)

    # Encabezados de la tabla
    tk.Label(tabla, text="Nombre", font=("Helvetica", 12)).grid(row=0, column=0, padx=10, pady=10)
    tk.Label(tabla, text="Proveedor", font=("Helvetica", 12)).grid(row=0, column=1, padx=10, pady=10)
    tk.Label(tabla, text="Stock", font=("Helvetica", 12)).grid(row=0, column=2, padx=10, pady=10)
    tk.Label(tabla, text="Precio Unitario", font=("Helvetica", 12)).grid(row=0, column=3, padx=10, pady=10)
    tk.Label(tabla, text="Código de Barras", font=("Helvetica", 12)).grid(row=0, column=4, padx=10, pady=10)

    # Mostrar los productos
    productos = obtener_productos_alimentos()
    mostrar_productos(tabla, productos)

# ---------------------------------------- Función para mostrar productos en la tabla ----------------------------------------
def mostrar_productos(tabla, productos):
    # Elimina el contenido anterior
    for widget in tabla.winfo_children():
        widget.destroy()
    
    # Encabezados de la tabla
    tk.Label(tabla, text="Nombre", font=("Helvetica", 12)).grid(row=0, column=0, padx=10, pady=10)
    tk.Label(tabla, text="Proveedor", font=("Helvetica", 12)).grid(row=0, column=1, padx=10, pady=10)
    tk.Label(tabla, text="Stock", font=("Helvetica", 12)).grid(row=0, column=2, padx=10, pady=10)
    tk.Label(tabla, text="Precio Unitario", font=("Helvetica", 12)).grid(row=0, column=3, padx=10, pady=10)
    tk.Label(tabla, text="Código de Barras", font=("Helvetica", 12)).grid(row=0, column=4, padx=10, pady=10)
    
    # Rellenar la tabla con productos
    for i, producto in enumerate(productos):
        for j, valor in enumerate(producto):
            tk.Label(tabla, text=valor).grid(row=i+1, column=j, padx=10, pady=5)


# ---------------------------------------- Función para obtener productos por categoría "Medicamentos" ----------------------------------------
def obtener_productos_medicamentos(filtros=None):
    conn = conectar_bd()
    productos = []
    query = "SELECT nombre_producto, proveedor, stock, precio_unitario, codigo_barras FROM productos WHERE area = 'Medicamentos'"
    
    condiciones = []
    parametros = []
    
    if filtros:
        if filtros.get('nombre'):
            condiciones.append("nombre_producto ILIKE %s")
            parametros.append(f"%{filtros['nombre']}%")
        if filtros.get('proveedor'):
            condiciones.append("proveedor ILIKE %s")
            parametros.append(f"%{filtros['proveedor']}%")
        if filtros.get('stock'):
            condiciones.append("stock = %s")
            parametros.append(filtros['stock'])
        if filtros.get('codigo_barras'):
            condiciones.append("codigo_barras = %s")
            parametros.append(filtros['codigo_barras'])

    if condiciones:
        query += " AND " + " AND ".join(condiciones)

    if conn:
        cursor = conn.cursor()
        cursor.execute(query, parametros)
        productos = cursor.fetchall()
        cursor.close()
        conn.close()

    return productos

# ---------------------------------------- Función para mostrar inventario de Medicamentos ----------------------------------------
def mostrar_inventario_medicamentos():
    ventana_medicamentos = tk.Toplevel()
    ventana_medicamentos.title("Inventario de Medicamentos")
    ventana_medicamentos.geometry("700x500")
    
    # Frame para filtros
    filtros_frame = tk.Frame(ventana_medicamentos)
    filtros_frame.pack(pady=10)
    
    # Campos de entrada para los filtros
    tk.Label(filtros_frame, text="Nombre:").grid(row=0, column=0, padx=5, pady=5)
    entrada_nombre = tk.Entry(filtros_frame)
    entrada_nombre.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(filtros_frame, text="Proveedor:").grid(row=0, column=2, padx=5, pady=5)
    entrada_proveedor = tk.Entry(filtros_frame)
    entrada_proveedor.grid(row=0, column=3, padx=5, pady=5)

    tk.Label(filtros_frame, text="Stock:").grid(row=1, column=0, padx=5, pady=5)
    entrada_stock = tk.Entry(filtros_frame)
    entrada_stock.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(filtros_frame, text="Código de Barras:").grid(row=1, column=2, padx=5, pady=5)
    entrada_codigo_barras = tk.Entry(filtros_frame)
    entrada_codigo_barras.grid(row=1, column=3, padx=5, pady=5)

    # Botón para aplicar filtros
    def aplicar_filtros_medicamentos():
        filtros = {
            'nombre': entrada_nombre.get(),
            'proveedor': entrada_proveedor.get(),
            'stock': entrada_stock.get(),
            'codigo_barras': entrada_codigo_barras.get(),
        }
        productos = obtener_productos_medicamentos(filtros)
        mostrar_productos(tabla, productos)

    boton_filtrar = tk.Button(filtros_frame, text="Buscar", command=aplicar_filtros_medicamentos)
    boton_filtrar.grid(row=2, column=0, columnspan=4, pady=10)

    # Frame para mostrar los productos
    tabla = tk.Frame(ventana_medicamentos)
    tabla.pack(pady=10)

    # Encabezados de la tabla
    tk.Label(tabla, text="Nombre", font=("Helvetica", 12)).grid(row=0, column=0, padx=10, pady=10)
    tk.Label(tabla, text="Proveedor", font=("Helvetica", 12)).grid(row=0, column=1, padx=10, pady=10)
    tk.Label(tabla, text="Stock", font=("Helvetica", 12)).grid(row=0, column=2, padx=10, pady=10)
    tk.Label(tabla, text="Precio Unitario", font=("Helvetica", 12)).grid(row=0, column=3, padx=10, pady=10)
    tk.Label(tabla, text="Código de Barras", font=("Helvetica", 12)).grid(row=0, column=4, padx=10, pady=10)

    # Mostrar los productos
    productos = obtener_productos_medicamentos()
    mostrar_productos(tabla, productos)

# ---------------------------------------- Función para obtener productos por categoría "Higiene" ----------------------------------------
def obtener_productos_higiene(filtros=None):
    conn = conectar_bd()
    productos = []
    query = "SELECT nombre_producto, proveedor, stock, precio_unitario, codigo_barras FROM productos WHERE area = 'Higiene'"
    
    condiciones = []
    parametros = []
    
    if filtros:
        if filtros.get('nombre'):
            condiciones.append("nombre_producto ILIKE %s")
            parametros.append(f"%{filtros['nombre']}%")
        if filtros.get('proveedor'):
            condiciones.append("proveedor ILIKE %s")
            parametros.append(f"%{filtros['proveedor']}%")
        if filtros.get('stock'):
            condiciones.append("stock = %s")
            parametros.append(filtros['stock'])
        if filtros.get('codigo_barras'):
            condiciones.append("codigo_barras = %s")
            parametros.append(filtros['codigo_barras'])

    if condiciones:
        query += " AND " + " AND ".join(condiciones)

    if conn:
        cursor = conn.cursor()
        cursor.execute(query, parametros)
        productos = cursor.fetchall()
        cursor.close()
        conn.close()

    return productos

# ---------------------------------------- Función para mostrar inventario de Higiene ----------------------------------------
def mostrar_inventario_higiene():
    ventana_higiene = tk.Toplevel()
    ventana_higiene.title("Inventario de Higiene")
    ventana_higiene.geometry("700x500")
    
    # Frame para filtros
    filtros_frame = tk.Frame(ventana_higiene)
    filtros_frame.pack(pady=10)
    
    # Campos de entrada para los filtros
    tk.Label(filtros_frame, text="Nombre:").grid(row=0, column=0, padx=5, pady=5)
    entrada_nombre = tk.Entry(filtros_frame)
    entrada_nombre.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(filtros_frame, text="Proveedor:").grid(row=0, column=2, padx=5, pady=5)
    entrada_proveedor = tk.Entry(filtros_frame)
    entrada_proveedor.grid(row=0, column=3, padx=5, pady=5)

    tk.Label(filtros_frame, text="Stock:").grid(row=1, column=0, padx=5, pady=5)
    entrada_stock = tk.Entry(filtros_frame)
    entrada_stock.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(filtros_frame, text="Código de Barras:").grid(row=1, column=2, padx=5, pady=5)
    entrada_codigo_barras = tk.Entry(filtros_frame)
    entrada_codigo_barras.grid(row=1, column=3, padx=5, pady=5)

    # Botón para aplicar filtros
    def aplicar_filtros_higiene():
        filtros = {
            'nombre': entrada_nombre.get(),
            'proveedor': entrada_proveedor.get(),
            'stock': entrada_stock.get(),
            'codigo_barras': entrada_codigo_barras.get(),
        }
        productos = obtener_productos_higiene(filtros)
        mostrar_productos(tabla, productos)

    boton_filtrar = tk.Button(filtros_frame, text="Buscar", command=aplicar_filtros_higiene)
    boton_filtrar.grid(row=2, column=0, columnspan=4, pady=10)

    # Frame para mostrar los productos
    tabla = tk.Frame(ventana_higiene)
    tabla.pack(pady=10)

    # Encabezados de la tabla
    tk.Label(tabla, text="Nombre", font=("Helvetica", 12)).grid(row=0, column=0, padx=10, pady=10)
    tk.Label(tabla, text="Proveedor", font=("Helvetica", 12)).grid(row=0, column=1, padx=10, pady=10)
    tk.Label(tabla, text="Stock", font=("Helvetica", 12)).grid(row=0, column=2, padx=10, pady=10)
    tk.Label(tabla, text="Precio Unitario", font=("Helvetica", 12)).grid(row=0, column=3, padx=10, pady=10)
    tk.Label(tabla, text="Código de Barras", font=("Helvetica", 12)).grid(row=0, column=4, padx=10, pady=10)

    # Mostrar los productos
    productos = obtener_productos_higiene()
    mostrar_productos(tabla, productos)
#---------------------------------Devoluciones---------------------------------------------------



# Función para obtener el historial de pedidos
def obtener_historial_pedidos(fecha=None):
    conn = conectar_bd()
    historial = []

    try:
        cursor = conn.cursor()
        if fecha:
            cursor.execute("SELECT id, fecha, ids_productos, total, cambio FROM compras WHERE fecha::date = %s", (fecha,))
        else:
            cursor.execute("SELECT id, fecha, ids_productos, total, cambio FROM compras")
        
        historial = cursor.fetchall()
    except Exception as e:
        print("Error al obtener el historial de pedidos:", e)
    finally:
        cursor.close()
        conn.close()

    return historial

# Función para mostrar el historial de pedidos
def mostrar_historial_pedidos():
    # Crear una nueva ventana
    historial_window = tk.Toplevel()
    historial_window.title("Historial de Pedidos")

    # Frame para mostrar los filtros
    frame_filtro = tk.Frame(historial_window)
    frame_filtro.pack(pady=10)

    tk.Label(frame_filtro, text="Filtrar por fecha (YYYY-MM-DD):").pack(side=tk.LEFT)
    fecha_entry = tk.Entry(frame_filtro)
    fecha_entry.pack(side=tk.LEFT, padx=5)
    btn_filtrar = tk.Button(frame_filtro, text="Filtrar", command=lambda: filtrar_historial(fecha_entry.get(), historial_window))
    btn_filtrar.pack(side=tk.LEFT)

    # Cargar todos los pedidos al abrir la ventana
    filtrar_historial(None, historial_window)

# Función para filtrar el historial por fecha
def filtrar_historial(fecha, ventana):
    # Limpiar la tabla antes de mostrar nuevos datos
    for widget in ventana.winfo_children():
        if isinstance(widget, tk.Frame) and widget.winfo_name() != 'frame_filtro':
            widget.destroy()

    # Obtener historial de pedidos filtrado por fecha
    pedidos = obtener_historial_pedidos(fecha)

    frame_pedidos = tk.Frame(ventana)
    frame_pedidos.pack(pady=10)

    # Encabezados de las columnas
    tk.Label(frame_pedidos, text="Número de Pedido", font=("Helvetica", 12)).grid(row=0, column=0, padx=5)
    tk.Label(frame_pedidos, text="Fecha", font=("Helvetica", 12)).grid(row=0, column=1, padx=5)
    tk.Label(frame_pedidos, text="Productos", font=("Helvetica", 12)).grid(row=0, column=2, padx=5)
    tk.Label(frame_pedidos, text="Devolución", font=("Helvetica", 12)).grid(row=0, column=3, padx=5)

    if not pedidos:  # Si no hay pedidos, mostrar un mensaje
        tk.Label(frame_pedidos, text="No se encontraron pedidos.").grid(row=1, column=0, columnspan=4, padx=5)
    else:
        for index, pedido in enumerate(pedidos):
            if len(pedido) != 5:
                print(f"Advertencia: El pedido tiene {len(pedido)} columnas, se esperaban 5.")
                continue  # O maneja el error como prefieras
            
            id_pedido, fecha, ids_productos, total_pagado, cambio = pedido
            
            # Verificar que ids_productos no sea None
            if ids_productos is not None:
                productos_lista = ids_productos.split(',')
            else:
                productos_lista = []  # Si es None, asignar una lista vacía

            # Mostrar datos del pedido
            tk.Label(frame_pedidos, text=id_pedido).grid(row=index + 1, column=0, padx=5)
            tk.Label(frame_pedidos, text=fecha).grid(row=index + 1, column=1, padx=5)
            tk.Label(frame_pedidos, text=", ".join(productos_lista)).grid(row=index + 1, column=2, padx=5)

            # Botón para hacer devolución
            btn_devolucion = tk.Button(frame_pedidos, text="Devolver", command=lambda id_pedido=id_pedido, total_pagado=total_pagado, cambio=cambio: procesar_devolucion(id_pedido, total_pagado, cambio, productos_lista))
            btn_devolucion.grid(row=index + 1, column=3, padx=5)

# Función para procesar la devolución
def procesar_devolucion(id_pedido, total_pagado, cambio, productos_lista):
    contrasena_gerente = obtener_contrasena_gerente()
    contrasena_ingresada = simpledialog.askstring("Contraseña del Gerente", "Ingrese la contraseña del gerente:", show='*')

    if contrasena_ingresada == contrasena_gerente:
        productos_info = obtener_productos_del_pedido(id_pedido)
        
        if productos_info:
            for producto_id, cantidad in productos_info:
                # Actualizar el stock del producto en la base de datos
                actualizar_stock_producto(producto_id, cantidad)
                
            # Eliminar el pedido de la tabla de compras
            eliminar_pedido(id_pedido)

            monto_a_regresar = total_pagado - cambio
            messagebox.showinfo("Devolución Aprobada", f"Se devolverá un monto de: {monto_a_regresar:.2f}")
        else:
            messagebox.showerror("Error", "No se encontraron productos para devolver.")
    else:
        messagebox.showerror("Error", "Contraseña incorrecta.")

def obtener_productos_del_pedido(id_pedido):
    conn = conectar_bd()
    productos_info = []

    try:
        cursor = conn.cursor()
        # Obtener la información de los productos y sus cantidades
        cursor.execute("SELECT ids_productos FROM compras WHERE id = %s", (id_pedido,))
        resultado = cursor.fetchone()

        if resultado and resultado[0]:
            ids_productos = resultado[0].split(',')
            # Supongamos que guardamos las cantidades en un campo adicional
            cursor.execute("SELECT cantidad FROM compras WHERE id = %s", (id_pedido,))
            cantidades = cursor.fetchone()

            if cantidades:
                cantidad_producto = cantidades[0]  # Asegúrate de que esto devuelva una lista de cantidades
                for idx, producto_id in enumerate(ids_productos):
                    # Aquí se agrega la cantidad que corresponde a cada producto
                    productos_info.append((producto_id, cantidad_producto[idx]))  # Asegúrate de que esto tenga sentido en tu implementación
    except Exception as e:
        print("Error al obtener productos del pedido:", e)
    finally:
        cursor.close()
        conn.close()

    return productos_info

def actualizar_stock_producto(producto_id, cantidad):
    conn = conectar_bd()

    try:
        cursor = conn.cursor()
        # Incrementar el stock del producto
        cursor.execute("UPDATE productos SET stock = stock + %s WHERE id = %s", (cantidad, producto_id))
        conn.commit()
    except Exception as e:
        print("Error al actualizar el stock del producto:", e)
    finally:
        cursor.close()
        conn.close()

def eliminar_pedido(id_pedido):
    conn = conectar_bd()

    try:
        cursor = conn.cursor()
        # Eliminar el pedido de la tabla de compras
        cursor.execute("DELETE FROM compras WHERE id = %s", (id_pedido,))
        conn.commit()
    except Exception as e:
        print("Error al eliminar el pedido:", e)
    finally:
        cursor.close()
        conn.close()

def obtener_contrasena_gerente():
    conn = conectar_bd()
    contrasena = None
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM usuarios WHERE rol = '2'")  # Ajusta el rol según tu implementación
        contrasena = cursor.fetchone()
        cursor.close()
        conn.close()
    return contrasena[0] if contrasena else None

#---------------------pedidosProvedores*---------------------------------


# Función para mostrar los productos y permitir hacer pedidos
def mostrar_pedido_proveedor():
    # Variables globales
    cantidad_a_pedir = []
    precios_productos = []  # Para almacenar precios de los productos
    productos_seleccionados = []  # Para almacenar productos seleccionados

    ventana_pedido = tk.Toplevel()
    ventana_pedido.title("Pedido a Proveedores")
    ventana_pedido.geometry("800x600")

    # Frame para filtros
    frame_filtros = tk.Frame(ventana_pedido)
    frame_filtros.pack(pady=10)

    tk.Label(frame_filtros, text="Proveedor:").grid(row=0, column=0, padx=10)
    entry_proveedor = tk.Entry(frame_filtros)
    entry_proveedor.grid(row=0, column=1, padx=10)

    tk.Label(frame_filtros, text="Código de Barras:").grid(row=0, column=2, padx=10)
    entry_codigo_barras = tk.Entry(frame_filtros)
    entry_codigo_barras.grid(row=0, column=3, padx=10)

    # Obtener productos filtrados por proveedor y código de barras
    def obtener_productos(filtro_proveedor="", filtro_codigo_barras=""):
        conn = conectar_bd()
        productos = []
        if conn:
            cursor = conn.cursor()
            query = """
                SELECT nombre_producto, stock, codigo_barras, proveedor, precio_unitario
                FROM productos
                WHERE 1=1
            """
            parametros = []

            if filtro_proveedor:
                query += " AND proveedor ILIKE %s"
                parametros.append(f"%{filtro_proveedor}%")
            if filtro_codigo_barras:
                query += " AND codigo_barras ILIKE %s"
                parametros.append(f"%{filtro_codigo_barras}%")

            cursor.execute(query, parametros)
            productos = cursor.fetchall()
            cursor.close()
            conn.close()
        return productos

    # Obtener la contraseña del gerente desde la base de datos
    def obtener_contrasena_gerente():
        conn = conectar_bd()
        contrasena = None
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT password FROM usuarios WHERE rol = '2'")
            contrasena = cursor.fetchone()
            cursor.close()
            conn.close()
        return contrasena[0] if contrasena else None

    # Actualizar stock en la base de datos
    def actualizar_stock(productos, cantidades):
        conn = conectar_bd()
        if conn:
            cursor = conn.cursor()
            for i, (producto, stock_actual) in enumerate(productos):
                if i < len(cantidades):
                    nueva_cantidad = stock_actual + cantidades[i]  # Sumar cantidad a stock actual
                    cursor.execute(
                        "UPDATE productos SET stock = %s WHERE nombre_producto = %s",
                        (nueva_cantidad, producto)
                    )
            conn.commit()  # Confirmar los cambios
            cursor.close()
            conn.close()

    # Función para realizar el pedido
    def realizar_pedido():
        nonlocal cantidad_a_pedir, precios_productos

        if not cantidad_a_pedir:  # Verificar si hay pedidos para realizar
            messagebox.showwarning("Advertencia", "No se ha agregado ninguna cantidad a pedir.")
            return

        contrasena_gerente = obtener_contrasena_gerente()
        if not contrasena_gerente:
            messagebox.showerror("Error", "No se encontró la contraseña del gerente.")
            return

        # Calcular total del pedido
        total_pedido = sum(cantidad_a_pedir[i] * precios_productos[i] for i in range(len(cantidad_a_pedir)))

        fecha_entrega = datetime.now() + timedelta(days=2)

        def verificar_contrasena():
            if entry_contrasena.get() == contrasena_gerente:
                # Actualizar stock en la base de datos
                actualizar_stock(productos_seleccionados, cantidad_a_pedir)
                messagebox.showinfo("Pedido realizado", f"Total: ${total_pedido:.2f}\nFecha de entrega: {fecha_entrega.strftime('%Y-%m-%d')}")
                ventana_autorizacion.destroy()
                ventana_pedido.destroy()  # Cerrar la ventana del pedido también

            else:
                messagebox.showerror("Error", "Contraseña incorrecta.")

        # Ventana de autorización
        ventana_autorizacion = tk.Toplevel()
        ventana_autorizacion.title("Autorización del Gerente")
        tk.Label(ventana_autorizacion, text="Contraseña del Gerente:").pack(pady=10)
        entry_contrasena = tk.Entry(ventana_autorizacion, show="*")
        entry_contrasena.pack(pady=10)
        tk.Button(ventana_autorizacion, text="Confirmar", command=verificar_contrasena).pack(pady=10)

    # Botón para buscar productos
    def buscar_productos():
        filtro_proveedor = entry_proveedor.get()
        filtro_codigo_barras = entry_codigo_barras.get()

        # Obtener productos filtrados
        productos = obtener_productos(filtro_proveedor, filtro_codigo_barras)

        # Limpiar tabla
        for widget in tabla.winfo_children():
            widget.destroy()

        # Encabezados de la tabla
        tk.Label(tabla, text="Producto", font=("Helvetica", 12)).grid(row=0, column=0, padx=10, pady=10)
        tk.Label(tabla, text="Stock Actual", font=("Helvetica", 12)).grid(row=0, column=1, padx=10, pady=10)
        tk.Label(tabla, text="Código de Barras", font=("Helvetica", 12)).grid(row=0, column=2, padx=10, pady=10)
        tk.Label(tabla, text="Precio", font=("Helvetica", 12)).grid(row=0, column=3, padx=10, pady=10)
        tk.Label(tabla, text="Pedido (Cantidad)", font=("Helvetica", 12)).grid(row=0, column=4, padx=10, pady=10)
        tk.Label(tabla, text="Agregar", font=("Helvetica", 12)).grid(row=0, column=5, padx=10, pady=10)

        # Rellenar la tabla con productos
        global productos_seleccionados  # Declarar la variable global
        productos_seleccionados = []  # Reiniciar la lista de productos seleccionados

        for i, (producto, stock, codigo_barras, proveedor, precio) in enumerate(productos):
            tk.Label(tabla, text=producto).grid(row=i + 1, column=0, padx=10, pady=5)
            tk.Label(tabla, text=stock).grid(row=i + 1, column=1, padx=10, pady=5)
            tk.Label(tabla, text=codigo_barras).grid(row=i + 1, column=2, padx=10, pady=5)
            tk.Label(tabla, text=f"${precio:.2f}").grid(row=i + 1, column=3, padx=10, pady=5)

            entry_pedido = tk.Entry(tabla)  # Campo editable
            entry_pedido.grid(row=i + 1, column=4, padx=10, pady=5)

            # Botón agregar
            tk.Button(tabla, text="Agregar", command=lambda entry=entry_pedido, prod=producto, stock=stock, price=precio: agregar_pedido(entry, prod, stock, price)).grid(row=i + 1, column=5, padx=10, pady=5)

    def agregar_pedido(entry, producto, stock_actual, precio):
        nonlocal cantidad_a_pedir, precios_productos, productos_seleccionados
        try:
            cantidad = int(entry.get())  # Obtener cantidad del campo correspondiente
            if cantidad < 0:
                messagebox.showerror("Error", "La cantidad no puede ser negativa.")
                return

            cantidad_a_pedir.append(cantidad)  # Agregar cantidad a la lista
            precios_productos.append(precio)  # Agregar precio del producto a la lista
            productos_seleccionados.append((producto, stock_actual))  # Almacena producto y su stock

        except ValueError:
            messagebox.showerror("Error", "Por favor ingrese un número válido.")

    # Botón de buscar
    tk.Button(frame_filtros, text="Buscar", command=buscar_productos).grid(row=0, column=4, padx=10)

    # Tabla para mostrar productos
    tabla = tk.Frame(ventana_pedido)
    tabla.pack(pady=20)

    # Botón para realizar pedido
    tk.Button(ventana_pedido, text="Realizar Pedido", command=realizar_pedido).pack(pady=20)

    ventana_pedido.mainloop()


# ---------------------------------------- Ventana Principal (Inicio de sesión) ----------------------------------------
ventana_principal = tk.Tk()
ventana_principal.title("Iniciar Sesión")
ventana_principal.geometry("400x300")

tk.Label(ventana_principal, text="Nombre de usuario:").pack(pady=5)
entry_username = tk.Entry(ventana_principal)
entry_username.pack(pady=5)

tk.Label(ventana_principal, text="Contraseña:").pack(pady=5)
entry_contrasena = tk.Entry(ventana_principal, show='*')
entry_contrasena.pack(pady=5)

tk.Button(ventana_principal, text="Iniciar Sesión", command=iniciar_sesion).pack(pady=10)

mostrar_dashboard_trabajador()
ventana_principal.mainloop()

