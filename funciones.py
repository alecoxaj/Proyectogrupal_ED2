from bisect import bisect_left, bisect_right  # Ayuda a insertar y buscar en listas ordenadas.
from math import ceil  # Permite redondear hacia arriba.


class NodoBPlus:
    def __init__(self, hoja=True):
        self.hoja = hoja  # True si contiene datos reales; False si es un nodo guía.
        self.claves = []  # Guarda las claves del nodo.
        self.hijos = []  # Guarda los hijos cuando el nodo es interno.
        self.siguiente = None  # Conecta una hoja con la siguiente.
        self.padre = None  # Permite regresar al padre durante una reparación.


class ArbolBPlus:
    def __init__(self, orden=4):
        if orden < 3:  # Comprueba que el orden sea válido.
            raise ValueError("El orden debe ser al menos 3.")

        self.orden = orden  # Máximo número de hijos.
        self.max_claves = orden - 1  # Máximo de claves por nodo.
        self.min_claves_hoja = ceil((orden - 1) / 2)  # Mínimo de claves en una hoja.
        self.min_hijos_interno = ceil(orden / 2)  # Mínimo de hijos internos.
        self.raiz = NodoBPlus(hoja=True)  # Al inicio, la raíz también es hoja.

    # BÚSQUEDA DE LA HOJA

    def _buscar_hoja(self, clave):
        nodo = self.raiz  # Comienza en la raíz.

        while not nodo.hoja:  # Continúa mientras no sea hoja.
            posicion = bisect_right(nodo.claves, clave)  # Determina el rango de la clave.
            nodo = nodo.hijos[posicion]  # Baja al hijo correspondiente.

        return nodo  # Devuelve la hoja encontrada.

    # BÚSQUEDA INDIVIDUAL

    def buscar(self, clave):
        hoja = self._buscar_hoja(clave)  # Localiza la hoja correcta.
        posicion = bisect_left(hoja.claves, clave)  # Busca dónde debería estar.

        return (
                posicion < len(hoja.claves)  # Comprueba que la posición exista.
                and hoja.claves[posicion] == clave  # Verifica que la clave coincida.
        )

    # INSERCIÓN

    def insertar(self, clave):
        if self.buscar(clave):  # Evita claves repetidas.
            return False

        hoja = self._buscar_hoja(clave)  # Localiza la hoja correcta.
        posicion = bisect_left(hoja.claves, clave)  # Calcula la posición ordenada.
        hoja.claves.insert(posicion, clave)  # Inserta la clave.

        if len(hoja.claves) > self.max_claves:  # Comprueba si se desbordó.
            self._dividir_hoja(hoja)  # Divide la hoja.

        self._recalcular_guias(self.raiz)  # Actualiza claves guía.
        return True

    def _dividir_hoja(self, hoja):
        punto = (len(hoja.claves) + 1) // 2  # Calcula el punto de división.

        nueva_hoja = NodoBPlus(hoja=True)  # Crea la hoja derecha.
        nueva_hoja.padre = hoja.padre  # Conserva el mismo padre.

        nueva_hoja.claves = hoja.claves[punto:]  # La derecha recibe la segunda parte.
        hoja.claves = hoja.claves[:punto]  # La izquierda conserva la primera.

        nueva_hoja.siguiente = hoja.siguiente  # La nueva hoja apunta a la siguiente.
        hoja.siguiente = nueva_hoja  # La hoja original apunta a la nueva.

        clave_guia = nueva_hoja.claves[0]  # Primera clave de la hoja derecha.
        self._insertar_en_padre(hoja, clave_guia, nueva_hoja)

    def _insertar_en_padre(self, izquierda, clave_guia, derecha):
        if izquierda is self.raiz:  # Si se dividió la raíz...
            nueva_raiz = NodoBPlus(hoja=False)  # Crea una raíz interna.
            nueva_raiz.claves = [clave_guia]  # Coloca la clave guía.
            nueva_raiz.hijos = [izquierda, derecha]  # Conecta ambas hojas.

            izquierda.padre = nueva_raiz  # Actualiza el padre izquierdo.
            derecha.padre = nueva_raiz  # Actualiza el padre derecho.
            self.raiz = nueva_raiz  # Sustituye la raíz.
            return

        padre = izquierda.padre  # Obtiene el padre actual.
        posicion = padre.hijos.index(izquierda)  # Localiza el hijo que se dividió.

        padre.claves.insert(posicion, clave_guia)  # Inserta la guía en el padre.
        padre.hijos.insert(posicion + 1, derecha)  # Inserta el nuevo hijo derecho.
        derecha.padre = padre  # Conecta el nuevo nodo con el padre.

        if len(padre.claves) > self.max_claves:  # Si el padre se desbordó...
            self._dividir_interno(padre)  # También debe dividirse.

    def _dividir_interno(self, nodo):
        centro = len(nodo.claves) // 2  # Busca la clave central.
        clave_que_sube = nodo.claves[centro]  # Esta clave sube al padre.

        nuevo_interno = NodoBPlus(hoja=False)  # Crea el nodo interno derecho.
        nuevo_interno.padre = nodo.padre  # Conserva el mismo padre.

        nuevo_interno.claves = nodo.claves[centro + 1:]  # Recibe claves de la derecha.
        nuevo_interno.hijos = nodo.hijos[centro + 1:]  # Recibe hijos de la derecha.

        for hijo in nuevo_interno.hijos:  # Recorre los hijos trasladados.
            hijo.padre = nuevo_interno  # Actualiza su nuevo padre.

        nodo.claves = nodo.claves[:centro]  # Conserva claves de la izquierda.
        nodo.hijos = nodo.hijos[:centro + 1]  # Conserva hijos de la izquierda.

        self._insertar_en_padre(nodo, clave_que_sube, nuevo_interno)

    # ELIMINACIÓN

    def eliminar(self, clave):
        hoja = self._buscar_hoja(clave)  # Busca la hoja correspondiente.
        posicion = bisect_left(hoja.claves, clave)  # Localiza la posición.

        if (
                posicion >= len(hoja.claves)
                or hoja.claves[posicion] != clave
        ):
            return False  # La clave no existe.

        hoja.claves.pop(posicion)  # Elimina la clave.

        if hoja is self.raiz:  # Si la raíz también es hoja...
            return True  # No necesita reparación.

        if len(hoja.claves) < self.min_claves_hoja:  # Comprueba el subdesbordamiento.
            self._reparar_hoja(hoja)  # Presta o fusiona.

        self._recalcular_guias(self.raiz)  # Actualiza todas las claves guía.
        return True

    # REPARAR UNA HOJA

    def _reparar_hoja(self, hoja):
        padre = hoja.padre  # Obtiene el padre.
        posicion = padre.hijos.index(hoja)  # Localiza la hoja.

        hermano_izquierdo = (
            padre.hijos[posicion - 1]
            if posicion > 0
            else None
        )

        hermano_derecho = (
            padre.hijos[posicion + 1]
            if posicion + 1 < len(padre.hijos)
            else None
        )

        if (
                hermano_izquierdo is not None
                and len(hermano_izquierdo.claves) > self.min_claves_hoja
        ):
            clave_prestada = hermano_izquierdo.claves.pop()  # Extrae la mayor clave izquierda.
            hoja.claves.insert(0, clave_prestada)  # La agrega al inicio de la hoja.
            return

        if (
                hermano_derecho is not None
                and len(hermano_derecho.claves) > self.min_claves_hoja
        ):
            clave_prestada = hermano_derecho.claves.pop(0)  # Extrae la menor clave derecha.
            hoja.claves.append(clave_prestada)  # La agrega al final de la hoja.
            return

        if hermano_izquierdo is not None:  # Si existe hermano izquierdo...
            hermano_izquierdo.claves.extend(hoja.claves)  # Une las claves.
            hermano_izquierdo.siguiente = hoja.siguiente  # Repara el enlace de hojas.

            padre.hijos.pop(posicion)  # Elimina la hoja fusionada.
            padre.claves.pop(posicion - 1)  # Elimina la guía correspondiente.

            self._reparar_interno(padre)  # Revisa el nodo padre.

        elif hermano_derecho is not None:  # Si solo existe el derecho...
            hoja.claves.extend(hermano_derecho.claves)  # Une las claves.
            hoja.siguiente = hermano_derecho.siguiente  # Repara el enlace.

            padre.hijos.pop(posicion + 1)  # Elimina el hermano derecho.
            padre.claves.pop(posicion)  # Elimina la clave guía.

            self._reparar_interno(padre)  # Revisa el nodo padre.

    # REPARAR NODOS INTERNOS

    def _reparar_interno(self, nodo):
        if nodo is self.raiz:  # Tratamiento especial de la raíz.
            if len(nodo.claves) == 0:  # Si quedó sin claves...
                self.raiz = nodo.hijos[0]  # Su hijo pasa a ser la raíz.
                self.raiz.padre = None  # La nueva raíz no tiene padre.
            return

        if len(nodo.hijos) >= self.min_hijos_interno:  # Si conserva suficientes hijos...
            return  # No necesita reparación.

        padre = nodo.padre  # Obtiene el padre.
        posicion = padre.hijos.index(nodo)  # Localiza el nodo.

        izquierdo = (
            padre.hijos[posicion - 1]
            if posicion > 0
            else None
        )

        derecho = (
            padre.hijos[posicion + 1]
            if posicion + 1 < len(padre.hijos)
            else None
        )

        if (
                izquierdo is not None
                and len(izquierdo.hijos) > self.min_hijos_interno
        ):
            hijo_movido = izquierdo.hijos.pop()  # Toma el último hijo izquierdo.
            hijo_movido.padre = nodo  # Actualiza su padre.

            nueva_guia = izquierdo.claves.pop()  # Toma la guía correspondiente.
            nodo.hijos.insert(0, hijo_movido)  # Inserta el hijo al inicio.
            nodo.claves.insert(0, padre.claves[posicion - 1])  # Baja la guía del padre.
            padre.claves[posicion - 1] = nueva_guia  # Sube la guía del hermano.
            return

        if (
                derecho is not None
                and len(derecho.hijos) > self.min_hijos_interno
        ):
            hijo_movido = derecho.hijos.pop(0)  # Toma el primer hijo derecho.
            hijo_movido.padre = nodo  # Actualiza su padre.

            nodo.hijos.append(hijo_movido)  # Agrega el hijo al final.
            nodo.claves.append(padre.claves[posicion])  # Baja la guía del padre.
            padre.claves[posicion] = derecho.claves.pop(0)  # Sube una guía nueva.
            return

        if izquierdo is not None:  # Fusiona con el hermano izquierdo.
            izquierdo.claves.append(
                padre.claves.pop(posicion - 1)
            )

            izquierdo.claves.extend(nodo.claves)  # Une las claves internas.

            for hijo in nodo.hijos:  # Recorre los hijos del nodo.
                hijo.padre = izquierdo  # Actualiza sus padres.

            izquierdo.hijos.extend(nodo.hijos)  # Une todos los hijos.
            padre.hijos.pop(posicion)  # Elimina el nodo fusionado.
            self._reparar_interno(padre)  # Revisa el padre.

        elif derecho is not None:  # Fusiona con el hermano derecho.
            nodo.claves.append(
                padre.claves.pop(posicion)
            )

            nodo.claves.extend(derecho.claves)  # Une las claves.

            for hijo in derecho.hijos:  # Recorre los hijos trasladados.
                hijo.padre = nodo  # Actualiza sus padres.

            nodo.hijos.extend(derecho.hijos)  # Une los hijos.
            padre.hijos.pop(posicion + 1)  # Elimina el hermano derecho.
            self._reparar_interno(padre)  # Revisa el padre.

    # ACTUALIZAR CLAVES GUÍA

    def _minimo_subarbol(self, nodo):
        while not nodo.hoja:  # Baja hasta la hoja izquierda.
            nodo = nodo.hijos[0]

        return nodo.claves[0]  # Devuelve la primera clave.

    def _recalcular_guias(self, nodo):
        if nodo.hoja:  # Las hojas no tienen guías.
            return

        for hijo in nodo.hijos:  # Recorre cada hijo.
            self._recalcular_guias(hijo)  # Actualiza niveles inferiores.

        nodo.claves = [
            self._minimo_subarbol(hijo)  # Inicio de cada hijo derecho.
            for hijo in nodo.hijos[1:]
        ]

    # BÚSQUEDA POR RANGO

    def buscar_rango(self, inicio, fin):
        if inicio > fin:  # Comprueba que el rango sea válido.
            inicio, fin = fin, inicio  # Intercambia los límites.

        hoja = self._buscar_hoja(inicio)  # Localiza la primera hoja.
        resultado = []  # Guarda las claves encontradas.

        while hoja is not None:  # Recorre hojas enlazadas.
            for clave in hoja.claves:  # Recorre sus claves.
                if inicio <= clave <= fin:  # Si pertenece al rango...
                    resultado.append(clave)  # La guarda.

                elif clave > fin:  # Si supera el límite...
                    return resultado  # Finaliza la búsqueda.

            hoja = hoja.siguiente  # Avanza a la siguiente hoja.

        return resultado  # Devuelve las coincidencias.

    # RECORRER TODAS LAS HOJAS

    def recorrer(self):
        nodo = self.raiz  # Comienza en la raíz.

        while not nodo.hoja:  # Baja a la hoja más izquierda.
            nodo = nodo.hijos[0]

        resultado = []  # Guarda todas las claves.

        while nodo is not None:  # Recorre las hojas enlazadas.
            resultado.extend(nodo.claves)  # Agrega sus claves.
            nodo = nodo.siguiente  # Avanza a la siguiente hoja.

        return resultado  # Devuelve las claves ordenadas.

    # MOSTRAR LA ESTRUCTURA

    def mostrar(self):
        self._mostrar(self.raiz, 0)  # Comienza desde la raíz.

    def _mostrar(self, nodo, nivel):
        sangria = "    " * nivel  # Representa la profundidad.

        tipo = "Hoja" if nodo.hoja else "Interno"  # Identifica el tipo de nodo.
        print(f"{sangria}{tipo}: {nodo.claves}")  # Muestra el nodo.

        if not nodo.hoja:  # Si tiene hijos...
            for hijo in nodo.hijos:  # Recorre cada uno.
                self._mostrar(hijo, nivel + 1)  # Los muestra recursivamente.


# Pruba de implementacion

arbol = ArbolBPlus(orden=4)

claves = [
    10, 20, 30, 40, 50,
    60, 70, 80, 90, 100
]

for clave in claves:
    arbol.insertar(clave)

print("ÁRBOL ORIGINAL")
arbol.mostrar()

print("\nRECORRIDO")
print(arbol.recorrer())

print("\nBÚSQUEDA POR RANGO: 25 A 75")
print(arbol.buscar_rango(25, 75))

print("\nELIMINAR 30")
arbol.eliminar(30)
arbol.mostrar()
print("Recorrido:", arbol.recorrer())

print("\nELIMINAR 40")
arbol.eliminar(40)
arbol.mostrar()
print("Recorrido:", arbol.recorrer())

print("\nBUSCAR 70")
print(arbol.buscar(70))

print("\nBUSCAR 35")
print(arbol.buscar(35))