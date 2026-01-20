# Tecno Tanks

## 1. Descripción General

**Tecno Tanks** es una reinterpretación moderna del clásico *Battle City (Tank 1990)*, desarrollada en **Python** utilizando la librería **Pygame**.
El proyecto tiene como propósito ofrecer una experiencia práctica para la aplicación de conceptos de **Sistemas Operativos** y **Sistemas Distribuidos**, integrando la **gestión de procesos**, **sincronización**, **comunicación entre hilos** y **control de recursos en tiempo real**.

El enfoque del desarrollo combina la jugabilidad retro con un diseño técnico avanzado, implementando concurrencia, control de acceso a recursos compartidos y comunicación en red cliente-servidor.

---

## 2. Arquitectura del Sistema

### 2.1 Estructura General

La arquitectura sigue un modelo **cliente-servidor distribuido**.
Cada jugador ejecuta un cliente Pygame que se comunica con un **servidor central** para mantener sincronizado el estado del juego (posiciones, disparos, colisiones y destrucción de estructuras).

![Arquitecture Diagram](/Arquitecture_diagram.png)

### 2.2 Componentes Principales

#### Cliente (Juego Pygame)

* Renderiza gráficos, animaciones y efectos visuales.
* Captura entradas del usuario (movimiento, disparo, interacción).
* Envía eventos al servidor (movimiento, ataque, destrucción).
* Actualiza el entorno local según los mensajes recibidos.

#### Servidor

* Gestiona el **estado global del juego**.
* Sincroniza posiciones, colisiones y eventos entre jugadores.
* Controla las **variables compartidas** y mantiene la consistencia del entorno.
* Supervisa los procesos de conexión, desconexión y sincronización de jugadores.

#### Recursos

* **Sprites y sonidos:** almacenados en la carpeta `/Assets/`.
* **Mapas CSV:** definen el terreno, muros, pasto, barreras y fortaleza.
* **Archivo `requirements.txt`:** lista las dependencias del proyecto.

### 2.3 Principios de Sistemas Operativos Aplicados

El proyecto tiene como objetivo demostrar conceptos fundamentales de sistemas operativos y distribuidos:

* **Gestión de procesos y estados:** tanques y proyectiles se ejecutan como procesos con estados (activo, destruido, respawn).
* **Sincronización de hilos:** control concurrente de animaciones, colisiones y disparos.
* **Variables compartidas:** estado global del mapa y recursos sincronizados.
* **Planificación y asignación de recursos:** control de acceso al CPU y tiempos de actualización.
* **Comunicación distribuida:** mensajes entre clientes y servidor mediante **web sockets**.
* **Monitoreo y tolerancia a la latencia:** ajustes de renderizado frente al retardo de red.

---

## 3. Instalación

### 3.1 Requisitos Previos

* **Python:** 3.10 o superior
* **Pip:** gestor de paquetes de Python
* **Sistemas compatibles:** Windows, Linux o macOS
* **Conexión a Internet:** requerida para modo en línea

### 3.2 Pasos de Instalación

```bash
# Clonar el repositorio
git clone https://github.com/DylanMA1/ProyectoSO1.git
cd ProyectoSO1

# Crear entorno virtual
python -m venv .venv

# Activar entorno virtual
# En Windows:
.venv\Scripts\activate

# En Linux / macOS:

# Si usas bash o zsh:
source .venv/bin/activate

# Si usas fish:
source .venv/bin/activate.fish

# Si usas csh o tcsh:
source .venv/bin/activate.csh

# Instalar dependencias
pip install -r requirements.txt

# Verificar instalación de Pygame
python -m pygame.examples.aliens
```

Si aparece una ventana de prueba, la instalación fue exitosa.

---

## 4. Despliegue y Ejecución

### 4.1 Modo Local (Offline)

Ejecutar el juego de manera individual:

```bash
python main.py
```

### 4.2 Modo Distribuido (Online)

Ejecutar el servidor en la nube o en otra máquina local:

```bash
python server.py
```

Los clientes requieren agregar la IP del servidor en la pantalla "Settings" para conectarse y sincronizar el estado global del juego (mapa, tanques, colisiones, etc.).

---

## 5. Descripción del Entorno y Recursos

| Carpeta / Archivo    | Descripción                                                   |
| -------------------- | ------------------------------------------------------------- |
| **Assets/**          | Sprites, sonidos y mapas del juego                            |
| **Code/**            | Código fuente principal                                       |
| **Code/Entities/**   | Clases de entidades (Jugador, Enemigo, Proyectil, Estructura) |
| **Code/Utilities/**  | Configuración general y funciones utilitarias                 |
| **requirements.txt** | Dependencias del proyecto                                     |
| **main.py**          | Cliente principal del juego                                   |
| **server.py**        | Lógica de sincronización en red                               |

---

## 6. Consideraciones Técnicas

* Motor de renderizado **Pygame**: 60 FPS por defecto.
* Comunicación en red mediante **Web Sockets** y paquetes **JSON**.
* Agrupación de sprites:

  * `visible_sprites`
  * `attackable_sprites`
  * `obstacle_sprites`
    
* Mapa basado en archivos CSV (`-1` representa espacio vacío).
* Soporte para destrucción de la fortaleza, sincronización de barreras y control de colisiones distribuidas.

---

## 7. Conclusión

**Tecno Tanks** combina diseño de videojuegos con conceptos avanzados de **programación concurrente** y **sistemas distribuidos**.
El proyecto demuestra cómo integrar **procesos**, **hilos**, **comunicación TCP** y **sincronización de recursos** dentro de un entorno interactivo y educativo, ofreciendo una experiencia que une teoría y práctica de manera lúdica.

---

📄 **Autors:** Dylan Molina Arroyo, Fabricio Alfaro
📆 **Versión:** 1.0.0

🔗 **Licencia:** MIT
