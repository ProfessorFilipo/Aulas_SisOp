# -*- coding: utf-8 -*-
"""Apaga a pasta _lab criada pelas estações (guarde antes o registro, se quiser)."""
from comum import *


def main():
    if MAC:
        marca = os.path.join(LAB, "volumes_mac.txt")
        if os.path.exists(marca):
            for vol in open(marca).read().split("\n"):
                if vol.strip() and os.path.ismount(vol.strip()):
                    cod, out = rodar(["hdiutil", "detach", vol.strip()])
                    if cod != 0:
                        cod, out = rodar(["hdiutil", "detach", "-force", vol.strip()])
                    print("   Volume %s desmontado: %s" % (vol.strip(), "ok" if cod == 0 else out.strip()))
    ponto = os.path.join(LAB, "e4", "ponto")
    if os.path.ismount(ponto):
        print(alerta("   %s ainda está montado. Desmontem antes de limpar." % ponto))
        return
    if os.path.exists(REGISTRO):
        destino = os.path.join(AQUI, "registro_da_dupla.md")
        shutil.copy(REGISTRO, destino)
        print("   Registro da dupla copiado para: %s" % destino)
    apagar_pasta(LAB)
    print("   Pasta de trabalho removida: %s" % ("ok" if not os.path.exists(LAB) else "restaram arquivos"))


if __name__ == "__main__":
    main()
