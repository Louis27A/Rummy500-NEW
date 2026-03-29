import random
from Turn import refillDeck, drawCard
def electionPhase(players, deck):
    print("Fase de Elección")
    active_players = [p for p in players if not p.isSpectator]
    if not active_players:
        return players # Casos raros donde todos sean espectadores

    availableCards = deck.drawInElectionPhase(len(active_players))  #Sacamos las Cartas para la fase de elección
    random.shuffle(availableCards)  #Mezclamos las Cartas que se van a elegir para que no estén en el mismo orden

    elections = {}  #Creamos un diccionario para almacenar las elecciones de los jugadores antes de la ronda
    for player, Card in zip(active_players, availableCards):
        elections[player] = Card  #Asignamos la Carta elegida a cada jugador
        print(f"{player} ha elegido la Carta: {Card}") #Indicamos qué Carta fue elegida

    #Con lo siguiente, se determinará el turno de la ronda para los jugadores dependiendo del valor numérico de la Carta que eligió cada uno
    order = sorted(
        elections.items(),
        key = lambda item: Card.values.index(item[1].value),
        reverse = True
    )
    playerOrder = [player for player, _ in order]  #Obtenemos el orden de los jugadores según sus elecciones
    
    # Agregar los espectadores al final de la lista para mantenerlos en el juego (aunque no jueguen)
    spectators = [p for p in players if p.isSpectator]
    playerOrder.extend(spectators)

    print("Orden de los jugadores:", playerOrder)
    return playerOrder
    #Devolvemos el orden de los jugadores para la ronda


def startRound(playersInOrder, screen): # Incluimos el atributo "screen" para la interfaz gráfica
    from Round import Round  #Importamos la clase Round aquí para evitar importaciones circulares
    roundInstance = Round(playersInOrder)  #Creamos una instancia de la clase Round
    roundInstance.initDeck()  #Inicializamos el mazo
    roundInstance.dealCards()  #Repartimos las cartas a los jugadores
    roundInstance.discardsAndTableDeck()  #Colocamos la primera carta en el montón de descartes
    roundInstance.showInitialState()  #Mostramos el estado inicial de la ronda

    #playerOrder = electionPhase(players, roundInstance.deck, screen, clockObj)  #Obtenemos el orden de los jugadores para la ronda

    return roundInstance, playersInOrder  #Devolvemos la instancia de la ronda y el orden de los jugadores

def mainGameLoop(screen, playersInOrder):
    """
    Lógica principal del juego:
      - Gestiona turnos.
      - Ofrece la carta del descarte a otros jugadores.
      - Controla compra, bajada, inserción y descarte.
    """
    #PRIMERO SE DECIDEN LOS TURNOS AL INICIAR LA RONDA. ES ALEATORIO DEBIDO A QUE YA NO HAY FASE DE ELECCIÓN.
    #EL PRIMER JUGADOR EN TURNO DEBE TOMAR UNA CARTA, YA SEA DEL MAZO O DEL DESCARTE. SI ELIGE TOMAR DEL DESCARTE,
    #NORMAL, AHÍ NO HAY PROBLEMA. PERO SI ELIGE TOMAR DEL MAZO, LOS DEMÁS JUGADORES DEBEN DECIDIR SI QUIEREN COMPRAR ESA CARTA O NO. 
    #SI ALGUNO DECIDE COMPRARLA, SE LA LLEVA Y EL JUGADOR EN TURNO TOMA LA CARTA DEL MAZO NORMALMENTE, EN UN PLAZO DE 7 SEGUNDOS. 
    #SI NINGUNO DECIDE COMPRARLA EN ESE TIEMPO, SIMPLEMENTE EL JUGADOR EN TURNO TOMA DEL MAZO Y SIGUE CON SU TURNO NORMAL.
    #UNA VEZ AHÍ, EL JUGADOR EN TURNO DEBE DECIDIR SI BAJARSE O NO, EN CASO DE TENER LA OPORTUNIDAD DE HACERLO.
    #SI ELIGE BAJARSE, COLOCARÁ LAS CARTAS SOBRE LA MESA. INDEPENDIENTEMENTE DE SI LO HACE O NO, DEBE
    #DESCARTAR UNA CARTA DESPUÉS.
    #A CONTINUACIÓN, SE LE PASA EL TURNO AL SIGUIENTE JUGADOR EN EL ORDEN DEL ARRAY, Y ASÍ SE SIGUE EL JUEGO
    #HASTA QUE ALGUIEN SE QUEDE SIN CARTAS. ES AHÍ DONDE TERMINA LA RONDA.
    roundObject = startRound(playersInOrder, screen)[0]
    currentRound = 1
    # Orden de jugadores fijo
    turn_order = playersInOrder[:]
    for p in turn_order:
        p.isHand = False
    #Aquí debería de leerse el orden de los jugadores según la fase de elección
    #turn_order.sort(key=lambda p: 0 if p.name == "Louis" else 1)
    discard_pile = roundObject.discards
    deck = roundObject.pile
    current_index = 0
    game_running = True
    plays_in_table = []  # Para almacenar las jugadas en la mesa, si es necesario para la IA

    # Estado inicial
    state = {
        "players": [],
        "deck_remaining": len(deck),
        "discard_top": discard_pile[-1] if discard_pile else None,
        "turn_order": [p.playerName for p in turn_order],
    }

    while game_running:
        players_info = [{'hand_size': len(p.playerHand)} for p in playersInOrder]
        current_player = turn_order[current_index]
        current_player.isHand = True
        print(f"\n-----------------TURNO DE {current_player.playerName}-------------------------")
        print(f"CARTAS DE {current_player.playerName}: {[str(c) for c in current_player.playerHand]}")
        print(f"CARTA DEL TOPE DEL DESCARTE: {roundObject.discards[-1] if roundObject.discards else None}")
        print(f"CARTAS RESTANTES EN PILE: {len(deck)}")
        print(f"SE ESTÁ JUGANDO LA RONDA NÚMERO {currentRound}")
        # Check if current player is AI
        if len(deck) == 0:
            refillDeck(roundObject)
            deck = roundObject.pile
        if hasattr(current_player, 'is_ai') and current_player.is_ai:
            should_draw_discard = current_player.decide_draw_source(
                discard_pile[-1] if discard_pile else None,
                len(deck),
                players_info
            )
            #TENGO QUE SEGUIR ANALIZANDO LAS VALIDACIONES DE CADA PROCESO, PARA PODER
            #PROBAR DESPUÉS EL ENTRENAMIENTO DE LA IA Y VERIFICAR SI TODO VA EN ORDEN.
            #DE SER EL CASO, PASARÍA A IMPLEMENTARLO EN UI2
            if should_draw_discard and discard_pile:
                if not current_player.cardDrawn:
                    # Draw from discard
                    drawCard(current_player, roundObject, fromDiscards=True)
                    current_player.playerHand = roundObject.hands[current_player.playerId]
                    print(f"EL JUGADOR {current_player.playerName} TOMÓ EL DESCARTEEEEE")
                    print(f"MANO DE ESE JUGADOR DESPUÉS DE TOMAR EL DESCARTE: {[str(c) for c in current_player.playerHand]}")
                    current_player.cardDrawn = True
                else:
                    print(f"EL JUGADOR {current_player.playerName} YA TOMÓ UNA CARTA ANTERIORMENTE")
            else:
                if not current_player.cardDrawn:
                    otherPlayers = [p for p in playersInOrder if p != current_player]
                    # Draw from deck
                    for i in range(len(otherPlayers)):
                        buyDecision = otherPlayers[i].decide_buy_card(roundObject.discards[-1], otherPlayers[i].calculatePointsAI(), playersInOrder)
                        if buyDecision:
                            current_player.canDiscard = False
                            if i == 0:

                                otherPlayers[i].buyCard(roundObject)
                                break
                            elif i == 1:
                                decision = otherPlayers[i-1].decide_buy_card(roundObject.discards[-1], otherPlayers[i-1].calculatePointsAI(), playersInOrder)
                                if decision:
                                    
                                    otherPlayers[i-1].buyCard(roundObject)
                                    break
                                else:
                                    
                                    otherPlayers[i].buyCard(roundObject)
                                    break
                            elif i == 2:
                                decision = otherPlayers[i-2].decide_buy_card(roundObject.discards[-1], otherPlayers[i-2].calculatePointsAI(), playersInOrder)
                                if decision:
                                    
                                    otherPlayers[i-2].buyCard(roundObject)
                                    break
                                else:
                                    decision2 = otherPlayers[i-1].decide_buy_card(roundObject.discards[-1], otherPlayers[i-1].calculatePointsAI(), playersInOrder)
                                    if decision2:
                                        
                                        otherPlayers[i-1].buyCard(roundObject)
                                        break
                                    else:
                                        
                                        otherPlayers[i].buyCard(roundObject)
                                        break
                            elif i == 3:
                                decision = otherPlayers[i-3].decide_buy_card(roundObject.discards[-1], otherPlayers[i-3].calculatePointsAI(), playersInOrder)
                                if decision:
                                    
                                    otherPlayers[i-3].buyCard(roundObject)
                                    break
                                else:
                                    decision2 = otherPlayers[i-2].decide_buy_card(roundObject.discards[-1], otherPlayers[i-2].calculatePointsAI(), playersInOrder)
                                    if decision2:
                                        
                                        otherPlayers[i-2].buyCard(roundObject)
                                        break
                                    else:
                                        decision3 = otherPlayers[i-1].decide_buy_card(roundObject.discards[-1], otherPlayers[i-1].calculatePointsAI(), playersInOrder)
                                        if decision3:
                                            
                                            otherPlayers[i-1].buyCard(roundObject)
                                            break
                                        else:
                                            
                                            otherPlayers[i].buyCard(roundObject)
                                            break
                            elif i == 4:
                                decision = otherPlayers[i-4].decide_buy_card(roundObject.discards[-1], otherPlayers[i-4].calculatePointsAI(), playersInOrder)
                                if decision:
                                    
                                    otherPlayers[i-4].buyCard(roundObject)
                                    break
                                else:
                                    decision2 = otherPlayers[i-3].decide_buy_card(roundObject.discards[-1], otherPlayers[i-3].calculatePointsAI(), playersInOrder)
                                    if decision2:
                                        
                                        otherPlayers[i-3].buyCard(roundObject)
                                        break
                                    else:
                                        decision3 = otherPlayers[i-2].decide_buy_card(roundObject.discards[-1], otherPlayers[i-2].calculatePointsAI(), playersInOrder)
                                        if decision3:
                                            
                                            otherPlayers[i-2].buyCard(roundObject)
                                            break
                                        else:
                                            decision4 = otherPlayers[i-1].decide_buy_card(roundObject.discards[-1], otherPlayers[i-1].calculatePointsAI(), playersInOrder)
                                            if decision4:
                                                
                                                otherPlayers[i-1].buyCard(roundObject)
                                                break
                                            else:
                                                
                                                otherPlayers[i].buyCard(roundObject)
                                                break
                            elif i == 5:
                                decision = otherPlayers[i-5].decide_buy_card(roundObject.discards[-1], otherPlayers[i-5].calculatePointsAI(), playersInOrder)
                                if decision:
                                    
                                    otherPlayers[i-5].buyCard(roundObject)
                                    break
                                else:
                                    decision2 = otherPlayers[i-4].decide_buy_card(roundObject.discards[-1], otherPlayers[i-4].calculatePointsAI(), playersInOrder)
                                    if decision2:
                                        
                                        otherPlayers[i-4].buyCard(roundObject)
                                        break
                                    else:
                                        decision3 = otherPlayers[i-3].decide_buy_card(roundObject.discards[-1], otherPlayers[i-3].calculatePointsAI(), playersInOrder)
                                        if decision3:
                                            
                                            otherPlayers[i-3].buyCard(roundObject)
                                            break
                                        else:
                                            decision4 = otherPlayers[i-2].decide_buy_card(roundObject.discards[-1], otherPlayers[i-2].calculatePointsAI(), playersInOrder)
                                            if decision4:
                                                
                                                otherPlayers[i-2].buyCard(roundObject)
                                                break
                                            else:
                                                decision5 = otherPlayers[i-1].decide_buy_card(roundObject.discards[-1], otherPlayers[i-1].calculatePointsAI(), playersInOrder)
                                                if decision5:
                                                    
                                                    otherPlayers[i-1].buyCard(roundObject)
                                                    break
                                                else:
                                                    
                                                    otherPlayers[i].buyCard(roundObject)
                                                    break
                            elif i == 6:
                                decision = otherPlayers[i-6].decide_buy_card(roundObject.discards[-1], otherPlayers[i-6].calculatePointsAI(), playersInOrder)
                                if decision:
                                    
                                    otherPlayers[i-6].buyCard(roundObject)
                                    break
                                else:
                                    decision2 = otherPlayers[i-5].decide_buy_card(roundObject.discards[-1], otherPlayers[i-5].calculatePointsAI(), playersInOrder)
                                    if decision2:
                                        
                                        otherPlayers[i-5].buyCard(roundObject)
                                        break
                                    else:
                                        decision3 = otherPlayers[i-4].decide_buy_card(roundObject.discards[-1], otherPlayers[i-4].calculatePointsAI(), playersInOrder)
                                        if decision3:
                                            
                                            otherPlayers[i-4].buyCard(roundObject)
                                            break
                                        else:
                                            decision4 = otherPlayers[i-3].decide_buy_card(roundObject.discards[-1], otherPlayers[i-3].calculatePointsAI(), playersInOrder)
                                            if decision4:
                                                
                                                otherPlayers[i-3].buyCard(roundObject)
                                                break
                                            else:
                                                decision5 = otherPlayers[i-2].decide_buy_card(roundObject.discards[-1], otherPlayers[i-2].calculatePointsAI(), playersInOrder)
                                                if decision5:
                                                    
                                                    otherPlayers[i-2].buyCard(roundObject)
                                                    break
                                                else:
                                                    decision6 = otherPlayers[i-1].decide_buy_card(roundObject.discards[-1], otherPlayers[i-1].calculatePointsAI(), playersInOrder)
                                                    if decision6:
                                                        
                                                        otherPlayers[i-1].buyCard(roundObject)
                                                        break
                                                    else:
                                                        
                                                        otherPlayers[i].buyCard(roundObject)
                                                        break
                            elif i == 7:
                                decision = otherPlayers[i-7].decide_buy_card(roundObject.discards[-1], otherPlayers[i-7].calculatePointsAI(), playersInOrder)
                                if decision:
                                    
                                    otherPlayers[i-7].buyCard(roundObject)
                                    break
                                else:
                                    decision2 = otherPlayers[i-6].decide_buy_card(roundObject.discards[-1], otherPlayers[i-6].calculatePointsAI(), playersInOrder)
                                    if decision2:
                                        
                                        otherPlayers[i-6].buyCard(roundObject)
                                        break
                                    else:
                                        decision3 = otherPlayers[i-5].decide_buy_card(roundObject.discards[-1], otherPlayers[i-5].calculatePointsAI(), playersInOrder)
                                        if decision3:
                                            
                                            otherPlayers[i-5].buyCard(roundObject)
                                            break
                                        else:
                                            decision4 = otherPlayers[i-4].decide_buy_card(roundObject.discards[-1], otherPlayers[i-4].calculatePointsAI(), playersInOrder)
                                            if decision4:
                                                
                                                otherPlayers[i-4].buyCard(roundObject)
                                                break
                                            else:
                                                decision5 = otherPlayers[i-3].decide_buy_card(roundObject.discards[-1], otherPlayers[i-3].calculatePointsAI(), playersInOrder)
                                                if decision5:
                                                    
                                                    otherPlayers[i-3].buyCard(roundObject)
                                                    break
                                                else:
                                                    decision6 = otherPlayers[i-2].decide_buy_card(roundObject.discards[-1], otherPlayers[i-2].calculatePointsAI(), playersInOrder)
                                                    if decision6:
                                                        
                                                        otherPlayers[i-2].buyCard(roundObject)
                                                        break
                                                    else:
                                                        decision7 = otherPlayers[i-1].decide_buy_card(roundObject.discards[-1], otherPlayers[i-1].calculatePointsAI(), playersInOrder)
                                                        if decision7:
                                                            
                                                            otherPlayers[i-1].buyCard(roundObject)
                                                            break
                                                        else:
                                                            
                                                            otherPlayers[i].buyCard(roundObject)
                                                            break
                        else:
                            print("NINGÚN JUGADOR COMPRÓ LA CARTA DEL DESCARTE")
                    if len(deck) == 0:
                        refillDeck(roundObject)
                        deck = roundObject.pile
                    drawCard(current_player, roundObject)
                    print(f"EL JUGADOR {current_player.playerName} TOMÓ DEL MAZO NORMAAAAAAL")
                    current_player.playerHand = roundObject.hands[current_player.playerId]
                    print(f"MANO DE ESE JUGADOR DESPUÉS DE TOMAR UNA CARTA: {[str(c) for c in current_player.playerHand]}")
                    current_player.cardDrawn = True
                    current_player.canDiscard = True
                else:
                    print(f"EL JUGADOR {current_player.playerName} YA TOMÓ UNA CARTA ANTERIORMENTE")
                                

            # Playing phase
            play = current_player.decide_play_cards(currentRound)
            if play and not current_player.downHand:
                # Execute the play on the board
                if not current_player.cardDrawn:
                # Si el jugador no ha tomado una carta, no puede jugar
                    print(f"{current_player.playerName} no ha tomado una carta y no puede jugar aún.")
                else:
                    if not hasattr(current_player, "jugadas_bajadas"):
                        current_player.jugadas_bajadas = []
                    if currentRound == 1:
                        seguidilla = play[1]
                        trio = play[0]
                        if not any(c.joker for c in seguidilla) and not current_player.isValidStraightF(seguidilla):
                            print("LA SEGUIDILLA NO ES VÁLIDA")
                        elif any(c.joker for c in seguidilla) and not current_player.isValidStraightFJoker(seguidilla):
                            print("LA SEGUIDILLA CON JOKER NO ES VÁLIDA")
                        elif not current_player.isValidTrioF(trio):
                            print("EL TRÍO NO ES VÁLIDO")
                        else:
                            if current_player.sortedStraight(seguidilla) == True: #DEBO QUITAR LO DE LAS ZONAS DE CARTAS Y EL VISUALHAND.
                                                                                    #CREO QUE LO MÁS INDICADO ES CAMBIARLO POR OTRAS COSAS. AHÍ VERÉ QUÉ SE LE HACE.
                                                                                    #SIMPLEMENTE TENGO QUE SEGUIR PROGRAMANDO ESTE CICLO DE JUEGO PARA QUE LA IA
                                                                                    #LO ENTIENDA PERFECTAMENTE :3
                                sortedStraights = seguidilla
                            else:
                                sortedStraights = current_player.sortedStraight(seguidilla)
                            current_player.jugadas_bajadas.append(sortedStraights)
                            current_player.jugadas_bajadas.append(trio)
                            for carta in trio + seguidilla:
                                if carta in current_player.playerHand:
                                    current_player.playerHand.remove(carta)
                            current_player.playMade.append(trio)
                            current_player.playMade.append(sortedStraights)
                            plays_in_table.append(trio) 
                            plays_in_table.append(sortedStraights) 
                            print(f"EL JUGADOR {current_player.playerName} SE BAJÓ CON LAS SIGUIENTES JUGADAS: {[[str(c) for c in play] for play in current_player.playMade]}")
                            current_player.downHand = True
                    elif currentRound == 2:
                        seguidilla1 = play[0]
                        seguidilla2 = play[1]
                        if not any(c.joker for c in seguidilla1) and not current_player.isValidStraightF(seguidilla1):
                            print("LA SEGUIDILLA 1 NO ES VÁLIDA")
                        elif any(c.joker for c in seguidilla1) and not current_player.isValidStraightFJoker(seguidilla1):
                            print("LA SEGUIDILLA 1 CON JOKER NO ES VÁLIDA")
                        elif not any(c.joker for c in seguidilla2) and not current_player.isValidStraightF(seguidilla2):
                            print("LA SEGUIDILLA 2 NO ES VÁLIDA")
                        elif any(c.joker for c in seguidilla2) and not current_player.isValidStraightFJoker(seguidilla2):
                            print("LA SEGUIDILLA 2 CON JOKER NO ES VÁLIDA")    
                        else:
                            if current_player.sortedStraight(seguidilla1) == True: #DEBO QUITAR LO DE LAS ZONAS DE CARTAS Y EL VISUALHAND.
                                                                                    #CREO QUE LO MÁS INDICADO ES CAMBIARLO POR OTRAS COSAS. AHÍ VERÉ QUÉ SE LE HACE.
                                                                                    #SIMPLEMENTE TENGO QUE SEGUIR PROGRAMANDO ESTE CICLO DE JUEGO PARA QUE LA IA
                                                                                    #LO ENTIENDA PERFECTAMENTE :3
                                sortedStraights1 = seguidilla1
                            else:
                                sortedStraights1 = current_player.sortedStraight(seguidilla)
                            if current_player.sortedStraight(seguidilla2) == True: #DEBO QUITAR LO DE LAS ZONAS DE CARTAS Y EL VISUALHAND.
                                                                                    #CREO QUE LO MÁS INDICADO ES CAMBIARLO POR OTRAS COSAS. AHÍ VERÉ QUÉ SE LE HACE.
                                                                                    #SIMPLEMENTE TENGO QUE SEGUIR PROGRAMANDO ESTE CICLO DE JUEGO PARA QUE LA IA
                                                                                    #LO ENTIENDA PERFECTAMENTE :3
                                sortedStraights2 = seguidilla2
                            else:
                                sortedStraights2 = current_player.sortedStraight(seguidilla2)
                            combined_check = sortedStraights1 + sortedStraights2
                            if current_player.isValidStraightF(combined_check, max_jokers= 4):
                                print("error, las dos seguidillas bajadas son una misma seguidilla partida en 2")
                            else:
                                current_player.jugadas_bajadas.append(sortedStraights1)
                                current_player.jugadas_bajadas.append(sortedStraights2)
                                for carta in sortedStraights1 + sortedStraights2:
                                    if carta in current_player.playerHand:
                                        current_player.playerHand.remove(carta)
                                current_player.playMade.append(sortedStraights2)
                                current_player.playMade.append(sortedStraights1)
                                plays_in_table.append(sortedStraights1) 
                                plays_in_table.append(sortedStraights2) 
                                print(f"EL JUGADOR {current_player.playerName} SE BAJÓ CON LAS SIGUIENTES JUGADAS: {[[str(c) for c in play] for play in current_player.playMade]}")
                                current_player.downHand = True
                    elif currentRound == 3:
                        trio1 = play[0]
                        trio2 = play[1]
                        trio3 = play[2]
                        if not current_player.isValidTrioF(trio1):
                            print("EL TRIO 1 NO ES VÁLIDO")
                        elif not current_player.isValidTrioF(trio2):
                            print("EL TRIO 2 NO ES VÁLIDO")
                        elif not current_player.isValidTrioF(trio3):
                            print("EL TRIO 3 NO ES VÁLIDO")
                        else:
                            # Obtenemos el valor de la primera carta que NO sea joker en cada zona
                            # next() busca el primer elemento que cumpla la condición, devuelve None si no encuentra
                            v1 = next((c.value for c in trio1 if not getattr(c, "joker", False)), None)
                            v2 = next((c.value for c in trio2 if not getattr(c, "joker", False)), None)
                            v3 = next((c.value for c in trio3 if not getattr(c, "joker", False)), None)
                            
                            # Comparamos si hay duplicados
                            if v1 == v2 or v1 == v3 or v2 == v3:
                                print("ERROR: No puedes bajar dos o más tríos del mismo valor.")
                            else:
                                current_player.jugadas_bajadas.append(trio1)
                                current_player.jugadas_bajadas.append(trio2)
                                current_player.jugadas_bajadas.append(trio3)
                                for carta in trio1 + trio2 + trio3:
                                    if carta in current_player.playerHand:
                                        current_player.playerHand.remove(carta)
                                current_player.playMade.append(trio1)
                                current_player.playMade.append(trio2)
                                current_player.playMade.append(trio3)
                                plays_in_table.append(trio1) 
                                plays_in_table(trio2) 
                                plays_in_table(trio3)
                                
                                print(f"EL JUGADOR {current_player.playerName} SE BAJÓ CON LAS SIGUIENTES JUGADAS: {[[str(c) for c in play] for play in current_player.playMade]}")
                                current_player.downHand = True
                    elif currentRound == 4:
                        trio1 = play[0]
                        trio2 = play[1]
                        seguidilla = play[2]

                        if not current_player.isValidTrioF(trio1):
                            print("EL TRIO 1 NO ES VÁLIDO")
                        elif not current_player.isValidTrioF(trio2):
                            print("EL TRIO 2 NO ES VÁLIDO")
                        if not any(c.joker for c in seguidilla) and not current_player.isValidStraightF(seguidilla):
                            print("LA SEGUIDILLA NO ES VÁLIDA")
                        elif any(c.joker for c in seguidilla) and not current_player.isValidStraightFJoker(seguidilla):
                            print("LA SEGUIDILLA CON JOKER NO ES VÁLIDA")
                        else:
                            v1 = next((c.value for c in trio1 if not getattr(c, "joker", False)), None)
                            v2 = next((c.value for c in trio2 if not getattr(c, "joker", False)), None)
                            
                            if v1 == v2:
                                print("ERROR: Los dos tríos deben ser de valores distintos.")
                            else:
                                complete = trio1 + trio2 + seguidilla
                                if len(complete) != len(current_player.playerHand):
                                    print("ERROR: En la cuarta ronda, debes bajarte con TODAS las cartas de tu mano")
                                else:
                                    if current_player.sortedStraight(seguidilla) == True: #DEBO QUITAR LO DE LAS ZONAS DE CARTAS Y EL VISUALHAND.
                                                                                                            #CREO QUE LO MÁS INDICADO ES CAMBIARLO POR OTRAS COSAS. AHÍ VERÉ QUÉ SE LE HACE.
                                                                                                            #SIMPLEMENTE TENGO QUE SEGUIR PROGRAMANDO ESTE CICLO DE JUEGO PARA QUE LA IA
                                                                                                            #LO ENTIENDA PERFECTAMENTE :3
                                        sortedStraights = seguidilla
                                    else:
                                        sortedStraights = current_player.sortedStraight(seguidilla)
                                    current_player.jugadas_bajadas.append(trio1)
                                    current_player.jugadas_bajadas.append(trio2)
                                    current_player.jugadas_bajadas.append(sortedStraights)
                                    for carta in trio1 + trio2 + sortedStraights:
                                        if carta in current_player.playerHand:
                                            current_player.playerHand.remove(carta)
                                    current_player.playMade.append(trio1)
                                    current_player.playMade.append(trio2)
                                    current_player.playMade.append(sortedStraights)
                                    plays_in_table.append(trio1) 
                                    plays_in_table(trio2) 
                                    plays_in_table(sortedStraights) 
                                    
                                    print(f"EL JUGADOR {current_player.playerName} SE BAJÓ CON LAS SIGUIENTES JUGADAS: {[[str(c) for c in play] for play in current_player.playMade]}")
                                    current_player.downHand = True

            # Insert phase
            if current_player.downHand and len(current_player.playerHand) > 0:
                play2 = current_player.decide_insert_card(plays_in_table)
                    
                if play2 and current_player.cardDrawn:
                    targetPlayer = None
                    for p in plays_in_table:
                        for player in playersInOrder:
                            if player.playMade == p:
                                targetPlayer = player
                                break
                    print("targetPlayer de la inserción:", targetPlayer)
                    if targetPlayer:
                        print(f"ÍNDICE INICIAL PARA INSERTAR: {play2[0]}")
                        idx = play2[0] - 1
                        jugada = current_player.insertCard(targetPlayer, play2[0], play2[1], play2[2])
                        if not jugada:
                            print("LA INSERCIÓN NO FUE VÁLIDAAAAAAAAAAAAAAAAAAAAAAAA")
                
                play3 = current_player.decide_substitute_joker(plays_in_table)
                if play3:
                    targetPlayer2 = None
                    for p in plays_in_table:
                        for player in playersInOrder:
                            if p[0] == player.playerName:
                                targetPlayer2 = player
                                break
                    if targetPlayer2: 
                        current_player.insertCard(targetPlayer2, play3[0], play3[1], None, None)


            # Discard phase
            card_to_discard = list([current_player.decide_discard()])
            if card_to_discard and current_player.cardDrawn and len(current_player.playerHand) > 0 and current_player.isHand:
                current_player.discardCard(card_to_discard, roundObject)
                current_player.cardDrawn = False
                current_player.isHand = False
                roundObject.lastDiscardPlayer = current_player
                if len(current_player.playerHand) == 0:
                    current_player.winner = True
                    print(f"FIN DE LA RONDA {currentRound}. El ganador fue {current_player.playerName}")
                    print(f"INICIANDO LA RONDA NÚMERO {currentRound}...")
                    if currentRound == 4:
                        currentRound = 1
                    else:
                        currentRound += 1
                    discard_pile = []
                    deck = []
                    roundObject = startRound(playersInOrder, screen)[0]
                    discard_pile = roundObject.discards
                    deck = roundObject.pile
                    for p in playersInOrder:
                        p.calculatePoints()
                        p.playerHand = []
                        p.playerBuy = False
                        p.cardDrawn = False
                        p.downHand = False
                        p.playMade = []
                        p.jugadas_bajadas = []
                        roundObject.lastDiscardPlayer = None
                        roundObject.refillCounter = 0
                        if p.playerPoints >= 500:
                            playersInOrder.remove(p)
                    if len(playersInOrder) == 1:
                        print(f"TENEMOS UN GANADOR!!!!! El ganador de la partida es: {playersInOrder[0].playerName}!!!! FELICIDADES!!!")
                        break

                if current_index == (len(playersInOrder) - 1):
                    current_index = 0
                else:
                    current_index += 1
                    current_player = None
