from funciones import ArbolBPlus, buscar, insertar, eliminar

temperaturas = ArbolBPlus(orden=4)

def insertar(arbol, clave):
    return arbol.insertar(clave)


def buscar(arbol, clave):
    return arbol.buscar(clave)


def eliminar(arbol, clave):
    return arbol.eliminar(clave)


def menu():
    while True:
        print("\n--- Historial de Temperaturas por intervalos ---")
        print("1. Insertar temperatura")
        print("2. Buscar temperatura")
        print("3. Eliminar temperatura")
        print("4. Mostrar estructura del árbol")
        print("5. Salir ")
        
        opcion = input("Ingrese una opción: ")
        
        if opcion == "1":
            try:
                temperatura = float(input("Ingrese la temperatura: "))
                if insertar(temperaturas, temperatura):
                    print("Temperatura insertada correctamente.")
                else:
                    print("La temperatura ya existe en el historial.")
            except ValueError:
                print("Error: Por favor, ingrese un número válido.")
                
        elif opcion == "2":
            try:
                temperatura = float(input("Ingrese la temperatura a buscar: "))
                if buscar(temperaturas, temperatura):
                    print(f"Temperatura encontrada: {temperatura}")
                else:
                    print("Temperatura no encontrada.")
            except ValueError:
                print("Error: Por favor, ingrese un número válido.")
                
        elif opcion == "3":
            try:
                temperatura = float(input("Ingrese la temperatura a eliminar: "))
                if eliminar(temperaturas, temperatura):
                    print("Temperatura eliminada correctamente.")
                else:
                    print("La temperatura no existe en el historial.")
            except ValueError:
                print("Error: Por favor, ingrese un número válido.")
                
        elif opcion == "4":
            print("Estructura del árbol:")
            temperaturas.mostrar()
        elif opcion == "5":
            print("Saliendo del programa...")
            break
            
        else:
            print("Opción no válida. Intente de nuevo.")

if __name__ == "__main__":
    menu()
