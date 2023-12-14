import serial
#pip install pyserial

# Configura el puerto serie para comunicarse con el GPS
port = "/dev/ttyUSB0"  # Asegúrate de que el puerto sea el correcto
baudrate = 9600  # La velocidad de comunicación del GPS
ser = serial.Serial(port, baudrate)

# Lee los datos del GPS
while True:
    line = ser.readline().decode('utf-8').strip()
    if line.startswith("$GPRMC"):
        data = line.split(",")
        if data[2] == 'V':
            # No hay datos válidos disponibles
            continue
        lat = float(data[3][:2]) + float(data[3][2:]) / 60.0
        lon = float(data[5][:3]) + float(data[5][3:]) / 60.0
        print("Latitud:", lat)
        print("Longitud:", lon)
        