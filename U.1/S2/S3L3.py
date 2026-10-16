import math

def perimetro():
    scelta = int(input("Scegli una forma (1 per quadrato / 2 per rettangolo / 3 per cerchio): "))

    if scelta == 1:
        lato = float(input("Fornisci il lato del quadrato: "))
        print("Il perimetro del quadrato è", lato * 4)

    elif scelta == 2:
        base = float(input("Fornisci la base: "))
        altezza = float(input("Fornisci l'altezza: "))
        print("Il perimetro del rettangolo è", base * 2 + altezza * 2)

    elif scelta == 3:
        raggio = float(input("Fornisci il raggio: "))
        print("La circonferenza del cerchio è", 2 * math.pi * raggio)

    else:
        print("Scelta non valida")

perimetro()