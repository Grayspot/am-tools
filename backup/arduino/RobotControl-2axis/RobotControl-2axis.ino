/*
 * Robot Control - 2 axis
 * 
 * Ce programme permet de piloter deux moteurs hybrides d'un robot 2 axes YZ en envoyant une consigne pulse et une consigne direction aux drivers associés.
 * Les moteurs sont munis d'encodeurs relatifs, et chaque axe dispose de deux capteurs fin de course mécanique.
 * Une consigne Enable est également envoyée aux drivers afin de les activer ou désactiver au besoin.
 * 
 * Les moteurs sont connectés sur les pins 10-11-12-13-A0-A1
 * Les encodeurs sont connectés sur les pins 2-3-4-5
 * Les capteurs de fin de course sont connectés sur les pins 6-7-8-9
 * Le frein est activé sur le pin enable de l'axe Z A1
 * 
 * Créé le 09/12/2016
 * Modifié le 08/02/2017
 * Par Jean-Philippe COUTURIER
 * 
 * Révision 1.0.0.0
 * 
 */

#include <Encoder.h>                          // Bibliothèque pour la gestion des encodeurs

Encoder axisYencoder (2, 4);                  // Encodeur de l'axe Y, sur pin d'interruption 2 et second pin 4
Encoder axisZencoder (3, 5);                  // Encodeur de l'axe Z, sur pin d'interruption 3 et second pin 5

const int startLimitYpin        = 6;          // pin capteur axe Y position début
const int endLimitYpin          = 7;          // pin capteur axe Y position fin
const int startLimitZpin        = 8;          // pin capteur axe Z position début
const int endLimitZpin          = 9;          // pin capteur axe Z position fin
const int directionYpin         = 10;         // pin direction axe Y (1 = gauche, 0 = droite)
const int directionZpin         = 11;         // pin direction axe Y (1 = haut, 0 = bas)
const int stepYpin              = 12;         // pin step axe Y
const int stepZpin              = 13;         // pin step axe Z
const int enableYpin            = A0;         // pin enable axe Y
const int enableZpin            = A5;         // pin enable axe Z
const int brakeZpin             = A1;         // pin frein

const int motorStepsPerRevolution     = 200;  // Moteur de type Nema 23, angle de pas 1.8°, configuré en standard
const int encoderPulsesPerRevolution  = 1993; // Encodeur relatif, ~2000 impulsions par tour (500 impulsions par voie)
const float travelMultiplicator       = 66;   // Entrainement par courroie, 66 mm par tour
const float speedMin        = 30;             // Vitesse minimale admissible, 30 mm/s
const float speedMax        = 100;            // Vitesse maximale admissible, 100 mm/s
const float speedInit       = 30;             // Vitesse imposée lors de la prise d'origine, 30 mm/s
const float minStrokeY      = 100;            // Longueur minimum de l'axe Y, en mm
const float minStrokeZ      = 100;            // Longueur minimum de l'axe Z, en mm
const float maxStrokeY      = 700;            // Longueur maximum de l'axe Y, en mm
const float maxStrokeZ      = 700;            // Longueur maximum de l'axe Z, en mm

float distancePerStep = 0.33;                 // Distance parcourue par un seul pas moteur, par défaut 0.33 mm
float speedTravel     = 40;                   // Vitesse utilisée lors des déplacements, par défaut 40 mm/s
float strokeY  = 700;                         // Course actuelle de l'axe Y, en mm
float strokeZ  = 700;                         // Course actuelle de l'axe Z, en mm
float positionAxisY     = 0;                  // Position actuelle sur l'axe Y, en mm
float positionAxisZ     = 0;                  // Position actuelle sur l'axe Z, en mm
float targetAxisY       = 0;                  // Position demandée sur l'axe Y, en mm
float targetAxisZ       = 0;                  // Position demandée sur l'axe Z, en mm
int directionAxisY      = 1;                  // Direction du mouvement sur l'axe Y, 1 => vers la gauche, 0 => vers la droite (origine)
int directionAxisZ      = 1;                  // Direction du mouvement sur l'axe Z, 1 => vers le haut, 0 => vers le bas (origine)
int encoderYposition    = 0;                  // Nombre d'impulsions envoyées par le codeur de l'axe Y
int encoderZposition    = 0;                  // Nombre d'impulsions envoyées par le codeur de l'axe Z
boolean startLimitAxisY = false;              // Capteur mécanique de fin course de l'axe Y, position début
boolean endLimitAxisY   = false;              // Capteur mécanique de fin course de l'axe Y, position fin
boolean startLimitAxisZ = false;              // Capteur mécanique de fin course de l'axe Z, position début
boolean endLimitAxisZ   = false;              // Capteur mécanique de fin course de l'axe Z, position fin
boolean enableAxisY     = false;              // Activation de l'axe Y
boolean enableAxisZ     = false;              // Activation de l'axe Z

boolean brakeZ          = true;               // Etat du frein, par défaut activé
boolean originsDefined  = false;              // Etat de la prise d'origine, false tant qu'elle n'est pas prise

String inputString      = "";                 // Chaine de caractères contenant ce qui arrive sur port série
String lastInputString  = "";                 // Chaine contenant la derniere commande recue
boolean stringComplete  = false;              // Indicateur pour indiquer que la chaine reçue est complète

unsigned long loopTime  = 0;                  // Variable pour la capture du temps de boucle
int cmdMode             = 0;                  // Indicateur de mode actif [0,1,2,3,4]
boolean stopAllMotion   = false;              // Variable prévue pour interrompre tous les mouvements

void setup() {
  // Affectation des entrées/sorties  
  pinMode(startLimitYpin,       INPUT);
  pinMode(endLimitYpin,         INPUT);
  pinMode(startLimitZpin,       INPUT);
  pinMode(endLimitZpin,         INPUT);
  pinMode(directionYpin,        OUTPUT);
  pinMode(directionZpin,        OUTPUT);
  pinMode(stepYpin,             OUTPUT);
  pinMode(stepZpin,             OUTPUT);
  pinMode(enableYpin,           OUTPUT);
  pinMode(enableZpin,           OUTPUT);
  pinMode(brakeZpin,            OUTPUT);

  // Initialisation des entrées/sorties
  startLimitAxisY   = digitalRead(startLimitYpin);
  endLimitAxisY     = digitalRead(endLimitYpin);
  startLimitAxisZ   = digitalRead(startLimitZpin);
  endLimitAxisZ     = digitalRead(endLimitZpin);
  digitalWrite(directionYpin,  LOW);
  digitalWrite(directionZpin,  LOW);
  digitalWrite(stepYpin,       LOW);
  digitalWrite(stepZpin,       LOW);
  digitalWrite(enableYpin,     HIGH);
  digitalWrite(enableZpin,     HIGH);
  digitalWrite(brakeZpin,      LOW);
  
  // Ouverture du port série
  Serial.begin(115200);
  while (!Serial) {
    ; // Attente d'une connexion sur le port série
  }

  // Capture de l'horloge
  loopTime = millis(); 
  
  establishContact();  // Envoi d'un message pour établir le contact jusqu'à ce que le PC réponde
}

/*
 * Boucle principale
 * Dernière modification : 13/01/2017
 */
void loop() {
  // Lecture des positions et capteurs
  readPositions();
  
  // Traitement de l'instruction reçue
  if (stringComplete) {
    //protection de boucle
    stringComplete = false;    

    // Rétablissement des mouvements
    stopAllMotion = false;
    
    // Découpage de la réponse et conversion en tableau de chaines de caractères
    String instructions[3];    
    StringSplit(inputString, ',', instructions, 3);
    int str_len = instructions[0].length() + 1;
    char instruction[str_len];
    instructions[0].toCharArray(instruction, instructions[0].length() + 1);
    
    // Execution de la fonction associée à la commande reçue
    if (strstr(instruction,"STOPMOTION") != NULL) { // Arret d'urgence
      cmdMode = 0;
      stopAllMotion = true;
    }
    
    if (strstr(instruction,"INITAXISORIGINS") != NULL && !cmdMode) { // Prise d'origine
      cmdMode = 1;
      originsDefined = initAxisOrigins();
    }

    if (strstr(instruction,"SETSPEED") != NULL && !cmdMode) { // Configuration de la vitesse de déplacement
      cmdMode = 2;
      float speedAsked = instructions[1].toFloat();
      setSpeedYZ(speedAsked);      
    }

    if (strstr(instruction,"SETSTROKE") != NULL && !cmdMode) { // Configuration de la course des axes
      cmdMode = 3;
      float strokeYasked = instructions[1].toFloat();
      float strokeZasked = instructions[2].toFloat();
      setStrokeYZ(strokeYasked, strokeZasked);      
    }
    
    if (strstr(instruction,"BRKENGAGE") != NULL && !cmdMode) { // Activation du frein
      cmdMode = 5;
      brakeControl(1);
      cmdMode = 0;
    }

    if (strstr(instruction,"BRKRELEASE") != NULL && !cmdMode) { // Désactivation du frein
      cmdMode = 6;
      brakeControl(0);
      cmdMode = 0;
    }

    if (strstr(instruction,"GOTOPOSITION") != NULL && !cmdMode && originsDefined) { // Déplacement du robot à la position indiquée
      cmdMode = 4;
      float positionYasked = instructions[1].toFloat();
      float positionZasked = instructions[2].toFloat();
      goToPositionYZ(positionYasked, positionZasked);
    }    

    
    inputString = "";
  }
  
  // Envoi des informations complètes sur l'état du robot
  // [encodeur Y, encodeur Z, position Y, position Z, vitesse, limite Y start, limite Y end, limite Z start, limite Z end, enable Y, enable Z, course Y, course Z, origins]  
  if(millis() > (loopTime + 100) ) { // Envoi toutes les 10 ms
    sendInformationsToPC();

    // Capture de l'horloge
    loopTime = millis();
  }   
}

/*
 * SerialEvent occurs whenever a new data comes in the
 * hardware serial RX.  This routine is run between each
 * time loop() runs, so using delay inside loop can delay
 * response.  Multiple bytes of data may be available.
 * Dernière modification : 24/01/2017
 */
void serialEvent() {  
  interrupts();
  while (Serial.available() && !stringComplete) {
    // Récupération du nouveau byte:
    char inChar = (char)Serial.read();    
    // Si le caractère reçu est une fin de ligne, on indique que la chaine est complète
    if (inChar == '\n') {
      stringComplete = true;
      lastInputString = inputString;
    }
    else
    {
      // Ajout à inputString:
      inputString += inChar;      
    }
  }  
  noInterrupts();
}

void establishContact() {
  while (Serial.available() <= 0) {
    Serial.println("bonjour");   // Envoi du mot bonjour
    delay(300);
  }
}

/*
 * Arrêt de tous les mouvements
 * Dernière modification : 13/01/2017
 */
void stopMotion()
{
  inputString = "";
  while (Serial.available() && !stringComplete) {
    // Récupération du nouveau byte:
    char inChar = (char)Serial.read();
    // Si le caractère reçu est une fin de ligne, on indique que la chaine est complète
    if (inChar == '\n') {
      stringComplete = true;
      if( inputString == "X" )
      {
        stopAllMotion = true;    
        cmdMode = 0;
      }
    }
    else
    {
      // Ajout à inputString:
      inputString += inChar;
    }
  }  
}

/*
 * Lecture de la position des axes et de l'état des capteurs
 * Dernière modification : 13/01/2017
 */
void readPositions() {
  // status drivers
  enableAxisY = digitalRead(enableYpin);
  enableAxisZ = digitalRead(enableZpin);
  
  // capteurs
  startLimitAxisY   = digitalRead(startLimitYpin);
  endLimitAxisY     = digitalRead(endLimitYpin);
  startLimitAxisZ   = digitalRead(startLimitZpin);
  endLimitAxisZ     = digitalRead(endLimitZpin);

  // encodeurs
  interrupts();
  encoderYposition = axisYencoder.read();
  encoderZposition = axisZencoder.read();
  noInterrupts();

  // conversion en position métrique (mm)
  positionAxisY = ( encoderYposition * travelMultiplicator) / encoderPulsesPerRevolution;
  positionAxisZ = ( encoderZposition * travelMultiplicator) / encoderPulsesPerRevolution; 
}

/*
 * Lecture de la position des axes et de l'état des capteurs
 * Dernière modification : 10/12/2016
 */
void sendInformationsToPC() {  
    interrupts();
    Serial.print("ROBOTDATA,");
    Serial.print(encoderYposition);
    Serial.print(",");
    Serial.print(encoderZposition);
    Serial.print(",");
    Serial.print(positionAxisY);
    Serial.print(",");
    Serial.print(positionAxisZ);
    Serial.print(",");
    Serial.print(speedTravel);
    Serial.print(",");
    Serial.print(startLimitAxisY);
    Serial.print(",");
    Serial.print(endLimitAxisY);
    Serial.print(",");
    Serial.print(startLimitAxisZ);
    Serial.print(",");
    Serial.print(endLimitAxisZ);
    Serial.print(",");
    Serial.print(enableAxisY);
    Serial.print(",");
    Serial.print(enableAxisZ);
    Serial.print(",");
    Serial.print(strokeY);
    Serial.print(",");
    Serial.print(strokeZ);
    Serial.print(",");
    Serial.print(brakeZ);
    Serial.print(",");
    Serial.println(originsDefined);  
    //Serial.print(",");
    //Serial.println(lastInputString);      
    noInterrupts();
}

/*
 * Gestion du frein
 * Dernière modification : 24/01/2017
 */
void brakeControl(boolean brake)
{
  if(brake)
  {
    digitalWrite(brakeZpin, LOW);
    brakeZ = 1;
  }
  else
  {
    digitalWrite(brakeZpin, HIGH);
    brakeZ = 0;
  }
}

/*
 * Prise d'origines du robot
 * Dernière modification : 24/01/2017
 */
boolean initAxisOrigins() {
    
  // réglage de la direction de déplacement
    // Y
    digitalWrite(directionYpin,  HIGH); directionAxisY = true;  
    // Z
    digitalWrite(directionZpin,  LOW); directionAxisZ = false;
    
  // Activation des drivers moteurs
  digitalWrite(enableYpin,     LOW);
  digitalWrite(enableZpin,     LOW);

  // Désactivavtion du frein
  brakeControl(0);

  // durée de l'impulsion minimale (doit être supérieure à 5 µs)
  delayMicroseconds(10);

  // Capture de l'horloge  
  unsigned long loopTime   = micros();
  unsigned long sendTime   = millis();

  // Sécurité en cas de blocage robot ou d'arrêt d'urgence
  int blockTicks = 100;
  int lastPositionY = -100;
  int lastPositionZ = -100;

  // déplacement aux positions demandées  
  while((!startLimitAxisY || !startLimitAxisZ) && !stopAllMotion) {    
    // Lecture des positions et capteurs
    readPositions();

    // Vérification du buffer d'entrée du port série
    stopMotion();

    // Vérification du blocage ou de l'arrêt d'urgence = codeur qui ne bouge plus alors que la destination n'est pas atteinte
    if( (lastPositionY == encoderYposition && !startLimitAxisY) || (lastPositionZ == encoderZposition && !startLimitAxisZ) )
    { blockTicks--; }
    else
    { blockTicks = 100; }
    if( blockTicks <= 0 ) // arrêt des mouvements et sortie de la boucle
    { 
      stopAllMotion = true; 
      cmdMode = 0;
    }
    lastPositionY = encoderYposition;
    lastPositionZ = encoderZposition;

    // Envoi des infos au PC
    if( (millis() - sendTime) >= 500)
    {
      sendInformationsToPC();
      sendTime = millis();
    }

    // Récupération du temps d'exécution des autres instructions de la boucle
    unsigned long execDelay = micros() - loopTime;

    // Délai pour respecter la vitesse        
    long timeToWait = long((distancePerStep / speedTravel) * 1000000) - execDelay;    
    interrupts();
    if( timeToWait > 0 && timeToWait < 16000)
    {
      delayMicroseconds( timeToWait );    
    }
    else if( timeToWait > 0)
    {      
      delay( long(timeToWait / 1000) );          
    }
    else
    {
      delayMicroseconds(10);    
    }
    noInterrupts();

    // RAZ indicateur horloge
    loopTime = micros();
  
    // Activation des encodeurs
    interrupts();
    
    //déplacement sur Y    
    if(!startLimitAxisY && directionAxisY && !stopAllMotion) { // vers la gauche      
        digitalWrite(stepYpin,       HIGH);       
    }
    
    //déplacement sur Z    
    if(!startLimitAxisZ && !directionAxisZ && !stopAllMotion) { // vers le bas      
        digitalWrite(stepZpin,       HIGH);
    }

    // durée de l'impulsion minimale (doit être supérieure à 2.5 µs)
    delayMicroseconds(10);

    // reset des impulsions
    digitalWrite(stepYpin,       LOW);
    digitalWrite(stepZpin,       LOW);
        
    // Déctivation des encodeurs
    noInterrupts();
    
  }

  Serial.println("origins captured");

  // Activation de la lecture/écrture encodeur
  interrupts();

  // Mise à 0 des positions encodeurs
  axisYencoder.write(0);
  axisZencoder.write(0);

  // Désactivation de la lecture/écriture encodeur
  noInterrupts(); 

  // Activavtion du frein
  brakeControl(1);

  // Désactivation des drivers moteurs  
  digitalWrite(enableYpin,     HIGH);
  digitalWrite(enableZpin,     HIGH);  
  
  // réinitialisation du cmdMode
  cmdMode = 0;

  // Origine définie...
  if(startLimitAxisY && startLimitAxisZ) {
    return true;
  }
  // ...ou pas si un problème
  else {
     return false;    
  }    
}

/*
 * Réglage de la vitesse
 * Dernière modification : 10/01/2017
 */
void setSpeedYZ(float speedToSet) {
  if( speedToSet >= speedMin && speedToSet <= speedMax ) {
    speedTravel = speedToSet; // Vitesse envoyée par le PC
  }
  else {
    speedTravel = speedMin; // Vitesse minimale = 10 mm/s
  }     

  // réinitialisation du cmdMode
  cmdMode = 0;
}

/*
 * Réglage des courses
 * Dernière modification : 10/01/2017
 */
void setStrokeYZ(float strokeYtoSet, float strokeZtoSet) {
  if( strokeYtoSet >= minStrokeY && strokeYtoSet <= maxStrokeY ) {
    strokeY = strokeYtoSet; // Affectation de la nouvelle course sur Y
  }
  if( strokeZtoSet >= minStrokeZ && strokeZtoSet <= maxStrokeZ ) {
    strokeZ = strokeZtoSet; // Affectation de la nouvelle course sur Z
  }

  // réinitialisation du cmdMode
  cmdMode = 0;
}

/*
 * Déplacement du robot vers une position YZ
 * Dernière modification : 08/02/2017
 */
void goToPositionYZ(float positionYtoGo, float positionZtoGo) {
  boolean positionYreached = false;
  boolean positionZreached = false;

  // on vérifie si la position demandée n'excède pas la course de l'axe
  if( positionYtoGo < 0 ) { positionYtoGo = 0; }
  if( positionZtoGo < 0 ) { positionZtoGo = 0; }
  if( positionYtoGo > strokeY ) { positionYtoGo = strokeY; }
  if( positionZtoGo > strokeZ ) { positionZtoGo = strokeZ; }
  
  // conversion en position encodeur
  int encoderYpositionToGo = (int)( (positionYtoGo * encoderPulsesPerRevolution) / travelMultiplicator );
  int encoderZpositionToGo = (int)( (positionZtoGo * encoderPulsesPerRevolution) / travelMultiplicator );

  // initialissation des compteurs d'impulsions
  int pulserYcount = (int)( abs(positionYtoGo - positionAxisY) / distancePerStep);
  int pulserZcount = (int)( abs(positionZtoGo - positionAxisZ) / distancePerStep);

  // réglage de la direction de déplacement
    // Y
  if( encoderYposition < encoderYpositionToGo) { digitalWrite(directionYpin,  LOW); directionAxisY = false; } // déplacement vers la droite
  else { digitalWrite(directionYpin,  HIGH); directionAxisY = true; } // déplacement vers la gauche
    // Z
  if( encoderZposition < encoderZpositionToGo) { digitalWrite(directionZpin,  HIGH); directionAxisZ = true; } // déplacement vers le haut
  else { digitalWrite(directionZpin,  LOW); directionAxisZ = false; } // déplacement vers le bas
  
  // Activation des drivers moteurs
  digitalWrite(enableYpin,     LOW);
  digitalWrite(enableZpin,     LOW);

  // Désactivavtion du frein
  brakeControl(0);

  // durée de l'impulsion minimale (doit être supérieure à 5 µs)
  delayMicroseconds(10);

  // Capture de l'horloge
  unsigned long pulseTimeY = micros();
  unsigned long pulseTimeZ = micros();
  unsigned long loopTime   = micros();
  unsigned long sendTime   = millis();

  // Sécurité en cas de blocage robot ou d'arrêt d'urgence
  int blockTicks = 100;
  int lastPositionY = -100;
  int lastPositionZ = -100;

  // déplacement aux positions demandées  
  while((!positionYreached || !positionZreached) && !stopAllMotion) {    
    // Lecture des positions et capteurs
    readPositions();

    // Vérification du buffer d'entrée du port série
    stopMotion();

    // Vérification du blocage ou de l'arrêt d'urgence = codeur qui ne bouge plus alors que la destination n'est pas atteinte
    if( (lastPositionY == encoderYposition && !positionYreached) || (lastPositionZ == encoderZposition && !positionZreached) )
    { blockTicks--; }
    else
    { blockTicks = 100; }
    if( blockTicks <= 0 ) // arrêt des mouvements et sortie de la boucle
    { 
      stopAllMotion = true; 
      cmdMode = 0;
    }
    lastPositionY = encoderYposition;
    lastPositionZ = encoderZposition;

    // Vérification de la position par rapport à l'intervalle cible    
    if( encoderYpositionToGo - encoderYposition < 0 && !directionAxisY ) { positionYreached = true; } // vers la droite
    if( encoderYpositionToGo - encoderYposition > 0 && directionAxisY )  { positionYreached = true; } // vers la gauche
    if( encoderZpositionToGo - encoderZposition > 0 && !directionAxisZ ) { positionZreached = true; } // vers le bas
    if( encoderZpositionToGo - encoderZposition < 0 && directionAxisZ )  { positionZreached = true; } // vers le haut

    // Calcul du différentiel par rapport à la cible
    int diffPosY = abs(encoderYposition - encoderYpositionToGo);
    int diffPosZ = abs(encoderZposition - encoderZpositionToGo);

    // Correction du pulser si jamais des pas sont sautés
    if( (diffPosY - (10 * pulserYcount)) >= 10 ) { pulserYcount += (int)( ((diffPosY - (10 * pulserYcount)) / 10) ); } 
    if( (diffPosZ - (10 * pulserZcount)) >= 10 ) { pulserZcount += (int)( ((diffPosZ - (10 * pulserZcount)) / 10) ); } 

    // Envoi des infos au PC
    if( (millis() - sendTime) >= 500)
    {
      sendInformationsToPC();
      sendTime = millis();
    }

    // Récupération du temps d'exécution des autres instructions de la boucle
    unsigned long execDelay = micros() - loopTime;

    // Délai pour respecter la vitesse        
    long timeToWait = long((distancePerStep / speedTravel) * 1000000) - execDelay;    
    interrupts();
    if( timeToWait > 0 && timeToWait < 16000)
    {
      delayMicroseconds( timeToWait );    
    }
    else if( timeToWait > 0)
    {      
      delay( long(timeToWait / 1000) );          
    }
    else
    {
      delayMicroseconds(10);    
    }
    noInterrupts();

    // RAZ indicateur horloge
    loopTime = micros();

    // Position cible atteinte
    if( pulserYcount <= 0 && !positionYreached ) { positionYreached = true; } 
    if( pulserZcount <= 0 && !positionZreached ) { positionZreached = true; }     

    // Cas où on arrive en limite avant la position cible
    if( endLimitAxisY   && !directionAxisY  && !positionYreached ) {  positionYreached = true; } // vers la droite
    if( startLimitAxisY && directionAxisY   && !positionYreached ) {  positionYreached = true; } // vers la gauche
    if( startLimitAxisZ && !directionAxisZ  && !positionZreached ) {  positionZreached = true; } // vers le bas
    if( endLimitAxisZ   && directionAxisZ   && !positionZreached ) {  positionZreached = true; } // vers le haut
  
    // Activation des encodeurs
    interrupts();
    
    //déplacement sur Y
    if(!endLimitAxisY && !positionYreached && !directionAxisY && !stopAllMotion) { // vers la droite      
        digitalWrite(stepYpin,       HIGH);
        pulseTimeY = micros();  
        pulserYcount--;      
    }
    if(!startLimitAxisY && !positionYreached && directionAxisY && !stopAllMotion) { // vers la gauche      
        digitalWrite(stepYpin,       HIGH);
        pulseTimeY = micros();                
        pulserYcount--;
    }
    
    //déplacement sur Z
    if(!endLimitAxisZ && !positionZreached && directionAxisZ && !stopAllMotion) { // vers le haut      
        digitalWrite(stepZpin,       HIGH);
        pulseTimeZ = micros(); 
        pulserZcount--;       
    }
    if(!startLimitAxisZ && !positionZreached && !directionAxisZ && !stopAllMotion) { // vers le bas      
        digitalWrite(stepZpin,       HIGH);
        pulseTimeZ = micros();        
        pulserZcount--;
    }

    // durée de l'impulsion minimale (doit être supérieure à 2.5 µs)
    delayMicroseconds(10);

    // reset des impulsions
    digitalWrite(stepYpin,       LOW);
    digitalWrite(stepZpin,       LOW);
        
    // Déctivation des encodeurs
    noInterrupts();
    
  }

  Serial.println("move finished");

  // Activavtion du frein
  brakeControl(1);

  // Désactivation des drivers moteurs  
  digitalWrite(enableYpin,     HIGH);
  digitalWrite(enableZpin,     HIGH);  
  
  // réinitialisation du cmdMode
  cmdMode = 0;
}

/*
 * séparateur de texte et mise en tableau
 * Dernière modification : 13/01/2017
 */
int StringSplit(String sInput, char cDelim, String sParams[], int iMaxParams)
{
    int iParamCount = 0;
    int iPosDelim, iPosStart = 0;
    int loopSecure = 0;
    
    do {
        // Searching the delimiter using indexOf()
        iPosDelim = sInput.indexOf(cDelim,iPosStart);        
        if (iPosDelim >= (iPosStart+1)) {
            // Adding a new parameter using substring() 
            sParams[iParamCount] = sInput.substring(iPosStart,iPosDelim);
            iParamCount++;
            // Checking the number of parameters
            if (iParamCount >= iMaxParams) {
                return (iParamCount);
            }
            iPosStart = iPosDelim + 1;
        }
        loopSecure++;
    } while (iPosDelim >= 0 && loopSecure <= 10);
    if (iParamCount < iMaxParams) {
        // Adding the last parameter as the end of the line
        sParams[iParamCount] = sInput.substring(iPosStart);
        iParamCount++;
    }

    return (iParamCount);
}


