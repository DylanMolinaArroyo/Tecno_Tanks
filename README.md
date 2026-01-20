# Tecno Tanks

## 1. Overview

**Tecno Tanks** is a modern reinterpretation of the classic *Battle City (Tank 1990)*, developed in **Python** using the **Pygame** library.
The project aims to provide a hands-on experience for applying concepts from **Operating Systems** and **Distributed Systems**, integrating **process management**, **synchronization**, **inter-thread communication**, and **real-time resource control**.

The development focus combines retro gameplay with advanced technical design, implementing concurrency, shared resource access control, and client-server network communication.

---

## 2. System Architecture

### 2.1 General Structure

The architecture follows a **distributed client-server** model.
Each player runs a Pygame client that communicates with a **central server** to keep the game state synchronized (positions, shots, collisions, and structure destruction).

![Arquitecture Diagram](/Arquitecture_diagram.png)

### 2.2 Main Components

#### Client (Pygame Game)

* Renders graphics, animations, and visual effects.
* Captures user input (movement, shooting, interaction).
* Sends events to the server (movement, attack, destruction).
* Updates the local environment based on received messages.

#### Server

* Manages the **global game state**.
* Synchronizes positions, collisions, and events between players.
* Controls **shared variables** and maintains environment consistency.
* Supervises player connection, disconnection, and synchronization processes.

#### Resources

* **Sprites and sounds:** stored in the `/Assets/` folder.
* **CSV maps:** define terrain, walls, grass, barriers, and fortress.
* **`requirements.txt` file:** lists project dependencies.

### 2.3 Applied Operating Systems Principles

The project aims to demonstrate fundamental operating and distributed systems concepts:

* **Process and state management:** tanks and projectiles run as processes with states (active, destroyed, respawn).
* **Thread synchronization:** concurrent control of animations, collisions, and shots.
* **Shared variables:** synchronized global map state and resources.
* **Scheduling and resource allocation:** CPU access control and update times.
* **Distributed communication:** messages between clients and server via **web sockets**.
* **Monitoring and latency tolerance:** rendering adjustments for network delay.

---

## 3. Installation

### 3.1 Prerequisites

* **Python:** 3.10 or higher
* **Pip:** Python package manager
* **Compatible systems:** Windows, Linux, or macOS
* **Internet connection:** required for online mode

### 3.2 Installation Steps

```bash
# Clone the repository
git clone https://github.com/DylanMA1/ProyectoSO1.git
cd ProyectoSO1

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate

# On Linux / macOS:

# If using bash or zsh:
source .venv/bin/activate

# If using fish:
source .venv/bin/activate.fish

# If using csh or tcsh:
source .venv/bin/activate.csh

# Install dependencies
pip install -r requirements.txt

# Verify Pygame installation
python -m pygame.examples.aliens
```

If a test window appears, the installation was successful.

---

## 4. Deployment and Execution

### 4.1 Local Mode (Offline)

Run the game individually:

```bash
python main.py
```

### 4.2 Distributed Mode (Online)

Run the server in the cloud or on another local machine:

```bash
python server.py
```

Clients need to add the server IP on the "Settings" screen to connect and synchronize the global game state (map, tanks, collisions, etc.).

---

## 5. Environment and Resources Description

| Folder / File        | Description                                                   |
| -------------------- | ------------------------------------------------------------- |
| **Assets/**          | Game sprites, sounds, and maps                                |
| **Code/**            | Main source code                                              |
| **Code/Entities/**   | Entity classes (Player, Enemy, Projectile, Structure)         |
| **Code/Utilities/**  | General configuration and utility functions                   |
| **requirements.txt** | Project dependencies                                          |
| **main.py**          | Main game client                                              | 
| **server.py**        | Network synchronization logic                                 |

---

## 6. Technical Considerations

* **Pygame** rendering engine: 60 FPS by default.
* Network communication via **Web Sockets** and **JSON** packets.
* Sprite grouping:
  * `visible_sprites`
  * `attackable_sprites`
  * `obstacle_sprites`
* CSV file-based map (-1 represents empty space).
* Support for fortress destruction, barrier synchronization, and distributed collision control.

---

📄 **Autors:** Dylan Molina Arroyo, Fabricio Alfaro
📆 **Versión:** 1.0.0
