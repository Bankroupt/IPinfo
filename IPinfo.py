#!/usr/bin/env python3
import argparse, ipaddress, socket, sys, urllib.request, json, platform, subprocess, re

def clase_ip(ip_str: str):
    ip = ipaddress.ip_address(ip_str)
    if ip.version != 4:
        return "No aplicable (no-IPv4)", 'pública' if not ip.is_private else 'privada'
    first = int(ip_str.split('.')[0])
    if 1 <= first <= 126:
        clase = 'A'
    elif 128 <= first <= 191:
        clase = 'B'
    elif 192 <= first <= 223:
        clase = 'C'
    else:
        clase = 'Clase fuera de rango'
    privacidad = 'privada' if ip.is_private else 'pública'
    return clase, privacidad

def prefijo_de_red(mask: str):
    mask = mask.strip()
    if mask.startswith('/'):
        return int(mask.lstrip('/'))
    try:
        return ipaddress.ip_network(f"0.0.0.0/{mask}", strict=False).prefixlen
    except Exception:
        raise ValueError("Máscara incorrecta")

def get_local_ip(prefer_ipv6=False):
    family = socket.AF_INET6 if prefer_ipv6 else socket.AF_INET
    s = socket.socket(family, socket.SOCK_DGRAM)
    try:
        if prefer_ipv6:
            s.connect(('2001:db8::1', 80))
        else:
            s.connect(('198.51.100.1', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '::1' if prefer_ipv6 else '127.0.0.1'
    finally:
        s.close()
    return ip

def get_default_gateway_ip(prefer_ipv6=False) -> str:
    """
    Intentar obtener la puerta de enlace predeterminada leyendo la tabla de ruteo.
    Soporta Linux, macOS y Windows de forma básica.
    Fallback: estimación por convención (.1 IPv4) o feeback IPv6 (::1).
    """
    system = platform.system()
    try:
        if system == 'Linux':
            if prefer_ipv6:
                out = subprocess.check_output(['ip', '-6', 'route', 'show', 'default'], stderr=subprocess.DEVNULL, text=True)
                m = re.search(r'default via ([0-9a-fA-F:]+)', out)
            else:
                out = subprocess.check_output(['ip', 'route', 'show', 'default'], stderr=subprocess.DEVNULL, text=True)
                m = re.search(r'default via ([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)', out)
            if m:
                return m.group(1)
        elif system == 'Darwin':  # macOS
            if prefer_ipv6:
                out = subprocess.check_output(['netstat', '-rn', '-f', 'inet6'], stderr=subprocess.DEVNULL, text=True)
                m = re.search(r'default\s+([0-9a-fA-F:]+)', out)
            else:
                out = subprocess.check_output(['netstat', '-rn', '-f', 'inet'], stderr=subprocess.DEVNULL, text=True)
                m = re.search(r'default\s+([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)', out)
            if m:
                return m.group(1)
        elif system == 'Windows':
            out = subprocess.check_output(['route', 'print'], stderr=subprocess.DEVNULL, text=True, shell=True)
            if prefer_ipv6:
                m = re.search(r'0:0:0:0:0:0:0:0\s+([0-9a-fA-F:]+)', out)
            else:
                m = re.search(r'^\s*0\.0\.0\.0\s+0\.0\.0\.0\s+([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)\s', out, re.M)
            if m:
                return m.group(1)
    except Exception:
        pass

    if prefer_ipv6:
        return '::1'
    try:
        local = get_local_ip(prefer_ipv6=False)
        parts = local.split('.')
        parts[-1] = '1'
        return '.'.join(parts)
    except Exception:
        return '192.168.0.1'

def get_public_info(timeout=3) -> dict:
    services = [
        'https://ipinfo.io/json',
        'https://ifconfig.co/json'
    ]
    for url in services:
        try:
            with urllib.request.urlopen(url, timeout=timeout) as resp:
                data = resp.read().decode('utf-8')
                obj = json.loads(data)
                result = {}
                if 'ip' in obj:
                    result['ip'] = obj.get('ip')
                elif 'ipAddress' in obj:
                    result['ip'] = obj.get('ipAddress')
                if 'org' in obj:
                    result['isp'] = obj.get('org')
                elif 'isp' in obj:
                    result['isp'] = obj.get('isp')
                if 'country' in obj:
                    result['country'] = obj.get('country')
                if 'loc' in obj:
                    result['loc'] = obj.get('loc')
                if 'region' in obj:
                    result['region'] = obj.get('region')
                if 'city' in obj:
                    result['city'] = obj.get('city')
                if 'ip' in result:
                    return result
        except Exception:
            continue
    return {}

def main():
    p = argparse.ArgumentParser(description="Herramienta de terminal para una inspección básica de la red. Desarrollada por Rafael Loor D. (Telescom_Net).")
    group = p.add_mutually_exclusive_group()
    group.add_argument('--ip', help="Dirección IP (v4 o v6) para indicar su clase (solo IPv4) y si es privada. (10.0.0.5 o 2001:db8::1)")
    group.add_argument('--mask', help="Máscara de subred IPv4 (ej: 255.255.255.0 o /24) para mostrar prefijo.")
    group.add_argument('--all-ips', action='store_true', help="Mostrar IP local, IP del AP (gateway) y IP pública + ISP + país.")
    p.add_argument('--ipv6', action='store_true', help="Usar IPv6 para consultas locales y gateway cuando aplique.")
    args = p.parse_args()

    if args.ip:
        try:
            ip = ipaddress.ip_address(args.ip)
        except Exception:
            print("Dirección IP inválida")
            sys.exit(1)
        clase, privacidad = clase_ip(args.ip)
        print(f"IP: {args.ip} >> Clase: {clase} >> {privacidad}")
        return

    if args.mask:
        try:
            pref = prefijo_de_red(args.mask)
        except ValueError as e:
            print(e)
            sys.exit(1)
        print(f"Máscara: {args.mask} >> Prefijo: /{pref}")
        return

    if args.all_ips:
        local = get_local_ip()
        ap = get_default_gateway_ip()
        public_info = get_public_info()
        public_ip = public_info.get('ip', 'No disponible')
        isp = public_info.get('isp', 'No disponible')
        country = public_info.get('country', 'No disponible')
        loc = public_info.get('loc', 'No disponible')
        provincia = public_info.get('region', 'No disponible')
        sector = public_info.get('city', 'No disponible')
        print(f"IP local: {local}")
        print(f"IP del AP: {ap}")
        print(f"IP pública: {public_ip}")
        print(f"ISP: {isp}")
        print(f"País: {country}, {provincia}, {sector}")
        print(f"Localización: {loc}")
        return

    p.print_help()

if __name__ == '__main__':
    main()
