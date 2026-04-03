def check_alert(presence, rfid):
    if presence == 1 and rfid == 0:
        print(" ALERTE : Accès non autorisé détecté !")
    else:
        print("Accès normal")

# Test
check_alert(1, 0)