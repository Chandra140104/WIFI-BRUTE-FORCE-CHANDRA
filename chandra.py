import subprocess
import time
import requests

def scan_wifi_networks():
    """
    Memindai jaringan WiFi yang tersedia menggunakan perintah `netsh wlan show networks`.
    Mengembalikan daftar jaringan WiFi beserta informasi SSID, Authentication, dan Encryption.
    """
    result = subprocess.run(["netsh", "wlan", "show", "networks"], capture_output=True, text=True)
    if result.returncode == 0:
        networks = []
        current_network = {}
        for line in result.stdout.splitlines():
            if "SSID" in line and ":" in line:
                if current_network:
                    networks.append(current_network)
                current_network = {"SSID": line.split(":")[1].strip()}
            elif "Authentication" in line and ":" in line:
                current_network["Authentication"] = line.split(":")[1].strip()
            elif "Encryption" in line and ":" in line:
                current_network["Encryption"] = line.split(":")[1].strip()
        if current_network:
            networks.append(current_network)
        return networks
    else:
        print(" Gagal memindai jaringan WiFi.")
        return []

def display_available_wifi():
    """
    Menampilkan daftar jaringan WiFi yang tersedia.
    """
    print("\n🔍 Sedang memindai jaringan WiFi...\n")
    networks = scan_wifi_networks()
    if networks:
        print("📡 Daftar WiFi dalam jangkauan:")
        for i, network in enumerate(networks, start=1):
            print(f"{i}. SSID: {network.get('SSID', 'N/A')}")
            print(f"   Authentication: {network.get('Authentication', 'N/A')}")
            print(f"   Encryption: {network.get('Encryption', 'N/A')}")
            print()
    else:
        print(" Tidak ada jaringan WiFi yang ditemukan.")
    
def check_ssid_availability(ssid):
    """
    Memeriksa apakah SSID tertentu tersedia dalam daftar jaringan WiFi yang dipindai.
    """
    networks = scan_wifi_networks()
    available_ssids = [network.get("SSID") for network in networks]
    return ssid in available_ssids

def check_internet_connection():
    """
    Memeriksa koneksi internet dengan mencoba mengakses Google.
    """
    try:
        response = requests.get("https://www.google.com", timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False

def connect_to_wifi(ssid, password):
    """
    Mencoba menghubungkan ke jaringan WiFi dengan SSID dan password tertentu.
    Mengembalikan True jika berhasil terhubung, False jika gagal.
    """
    xml_profile = f"""<?xml version="1.0"?>
<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
    <name>{ssid}</name>
    <SSIDConfig>
        <SSID>
            <name>{ssid}</name>
        </SSID>
    </SSIDConfig>
    <connectionType>ESS</connectionType>
    <connectionMode>auto</connectionMode>
    <MSM>
        <security>
            <authEncryption>
                <authentication>WPA2PSK</authentication>
                <encryption>AES</encryption>
                <useOneX>false</useOneX>
            </authEncryption>
            <sharedKey>
                <keyType>passPhrase</keyType>
                <protected>false</protected>
                <keyMaterial>{password}</keyMaterial>
            </sharedKey>
        </security>
    </MSM>
</WLANProfile>"""

    with open(f"{ssid}.xml", "w") as f:
        f.write(xml_profile)
    
    add_profile_result = subprocess.run(["netsh", "wlan", "add", "profile", f"filename={ssid}.xml"], capture_output=True, text=True)
    if add_profile_result.returncode != 0:
        return False
    
    connect_result = subprocess.run(["netsh", "wlan", "connect", f"name={ssid}"], capture_output=True, text=True)
    if connect_result.returncode == 0:
        for _ in range(7):
            if check_internet_connection():
                return True
            time.sleep(1)
        return False
    else:
        return False

def try_multiple_passwords(ssid, passwords):
    total_passwords = len(passwords)
    for index, password in enumerate(passwords, start=1):
        percentage = (index / total_passwords) * 100
        print(f" Menghubungkan ke {ssid}... [{percentage:.1f}%]")
        if connect_to_wifi(ssid, password):
            print(f" Menghubungkan ke {ssid}... [100.0%]")  
            print(f"Berhasil terhubung ke SSID: {ssid}")
            print(f"Password: {password}")
            return True
        time.sleep(2)
    
    print(" Tidak ada password yang cocok.")
    return False

def wifi_menu():
    """
    Menu utama untuk memindai dan mencoba menghubungkan ke jaringan WiFi.
    """
    while True:
        display_available_wifi()  # Scan WiFi otomatis saat masuk menu ini.
        
        print("\n------------------------------")
        print("      MENU SCAN WIFI     ")
        print("------------------------------")
        print("1. Scan ulang WiFi")
        print("2. Masukkan SSID WiFi")
        print("3. Kembali ke Menu Utama")
        print("4. Keluar")
        print("------------------------------")
        
        sub_choice = input("Pilih opsi (1/2/3/4): ")
        
        if sub_choice == "1":
            continue  # Scan ulang WiFi dengan kembali ke awal loop
        elif sub_choice == "2":
            while True:
                ssid = input("\nMasukkan SSID WiFi: ")

                if not check_ssid_availability(ssid):
                    print(f" SSID '{ssid}' tidak ditemukan dalam jangkauan.")
                else:
                    passwords = input("Masukkan daftar password (pisahkan dengan koma): ").split(',')
                    passwords = [p.strip() for p in passwords]
                    success = try_multiple_passwords(ssid, passwords)

                    print("------------------------------")
                    print("1. Masukkan SSID dan Password Ulang")
                    print("2. Kembali ke Menu Sebelumnya")
                    print("3. Kembali ke Menu Utama")
                    print("4. Keluar")
                    print("------------------------------")
                    
                    post_choice = input("Pilih opsi (1/2/3/4): ")
                    
                    if post_choice == "1":
                        continue  # Kembali untuk memasukkan SSID baru
                    elif post_choice == "2":
                        break  # Kembali ke menu scan WiFi
                    elif post_choice == "3":
                        return  # Kembali ke menu utama
                    elif post_choice == "4":
                        exit(" Keluar dari program. Sampai jumpa!")
                    else:
                        print(" Pilihan tidak valid! Silakan pilih 1, 2, 3, atau 4.")
        elif sub_choice == "3":
            return  # Kembali ke menu utama
        elif sub_choice == "4":
            exit(" Keluar dari program. Sampai jumpa!")
        else:
            print(" Pilihan tidak valid! Silakan pilih 1, 2, 3, atau 4.")

def main_menu():
    """
    Menu utama program.
    """
    while True:
        print("\n" + "-" * 30)
        print("        WIFI CHANDRA        ")
        print("-" * 30)
        print("1. Mulai")
        print("2. Keluar")
        print("-" * 30)
        
        choice = input("Pilih opsi (1/2): ")
        
        if choice == "1":
            wifi_menu()
        elif choice == "2":
            print(" Keluar dari program. Sampai jumpa!")
            break
        else:
            print(" Pilihan tidak valid! Silakan pilih 1 atau 2.")

if __name__ == "__main__":
    main_menu()