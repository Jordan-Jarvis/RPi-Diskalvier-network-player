/*
Copyright (c) 2009 Jose M. Inesta <inesta@dlsi.ua.es>
Copyright (c) 2009 Pedro J. Ponce de Leon <pierre@dlsi.ua.es>
Copyright (c) 2009 Carlos Perez Sancho <cperez@dlsi.ua.es>
Copyright (c) 2009 Antonio Pertusa Ibanez <pertusa@dlsi.ua.es>
Copyright (c) 2009 David Rizo Valero <drizo@dlsi.ua.es>
Copyright (c) 2009 Tomas Perez Garcia <tperez@dlsi.ua.es>
Copyright (c) 2009 Universitat d'Alacant
*/


/****************************************************************************

Definici�n de las constantes que representaran los diversos mensajes del
General MIDI, lo pasaremos a n�mero para facilitar el trabajo.

****************************************************************************/

#ifndef TMIDI_H_
#define TMIDI_H_

#include <stdio.h>

#define FALSO		0
#define CIERTO          1

#define CANAL 		2
#define META  		3
#define SISTEMA		4

/* Lista de Datos de Canal */

#define NOTA_OFF	1128
#define NOTA_ON		1144
#define POST_POLIF	1160
#define CONTROL		1176
#define C_PROGRAMA	1192
#define POST_CANAL	1208
#define ALTURA		1224
#define SISEX		1225
#define MODULACION	1226

/* Lista de Meta Eventos */

#define NUM_SEC		200
#define TEXTO		201
#define COPYRIGTH	202
#define NOM_PISTA	203
#define NOM_INST	204
#define LETRA		205
#define POSICION	206
#define REFERENCIA	207
#define FIN_PISTA	208
#define AJUS_TEMPO	209
#define COMPAS		210
#define TONALIDAD	211
#define INFO_ESPEC	212
#define DESCONOCIDO	213


/****************************************************************************

Declaraci�n de los tipos de datos que usara la libreria. La idea es pasar de
un archivo General MIDI a una 'structura' que contenga todos los datos 
relebantes del mismo con el fin de poder trabajar con ellos de manera m�s
comoda.

****************************************************************************/

/***************************************************************************

Tipos de datos b�sicos.

***************************************************************************/


typedef char CODE4[5];
typedef unsigned long DOBLE;
typedef short int DATOS;
typedef unsigned char DATOS8;


/***************************************************************************

Estructura: TCabeceraMidi
Incluye los datos propios de la cabecera de los archivos General MIDI

***************************************************************************/


typedef struct {

   CODE4  id;
   DOBLE  size;
   DATOS  format;
   DATOS  numpistas;
   DATOS  delta;
   char* name;

} TCabeceraMidi;


/***************************************************************************

Estructura: TCabeceraPista
Incluye los datos propios de la cabecera de las pistas de 
los archivos General MIDI

***************************************************************************/


typedef struct {

   CODE4   id;
   DOBLE   size;
   DATOS8  *data;
   DATOS   numeventos;
   DATOS   numnotas;
} TCabeceraPista;

/***************************************************************************

Estructura: TEvento
informaci�n de cada uno de los eventos que componen una pista MIDI, 
guardamos todos los datos que nos pueden hacer falta sea cual sea el tipo
de evento (mensaje), los que no sean aplicables a un tipo de mensaje dado
se obviaran.

***************************************************************************/


typedef struct {

   DATOS   tipo; 
   DATOS   mensaje;
   DATOS   canal;
   DATOS   dato1;
   DATOS   dato2;
   DOBLE   dato3;
   char*   texto;
   int     tini;
   int	   t_delta;

} TEvento;

/***************************************************************************

Estructura: TNota
Informaci�n de las notas de una pista midi...
guardamos el momento de inicio, la duraci�n, la nota, la velocidad, etc.
***************************************************************************/

typedef struct {
  
  DATOS nota;
  DATOS velocidad;
  int   inicio;
  int   duracion;
  DATOS ligada; /* si es una continuaci�n de la nota anterior (cambio altura, por ejemplo)*/
  DATOS compas; /*compas al que pertenece (no implementado) */
  
} TNota;


/***************************************************************************

Estructura: TDescriptoresPista
Almacena los descriptores de una pista
***************************************************************************/

typedef struct {
  
  char *texto;/* le asignaremos un valor a cada posibilidad */ 
  int   nota_baja;  /* la nota mas baja que suena */
  int   longbytes;	
  float media;
  float desviacion;
  int   nota_alta;  /* la nota mas alta que suena */
  int   programa; /* el instrumento midi que esta sonando */
  int   canal;      /* canal por el que envia los datos */
  int   duracion;   /* duracion de la pista */
  int   d_sonido;   /* tiempo durante el que suena algo */
  float sonido;     /* tasa de uso de la pista */ 
  float polifonica; /* tasa de polifonia */
  float d_absoluta; /* tasa de duracion de la pista respecto a la duracion del midi */
  float s_absoluto; /* tasa de sonido respecto a la duracion del midi */	
  int   n_cambiosPrograma; /* numero de eventos cambio de programa de la pista */
  char *cambiosPrograma; /* string que indica el programa y el tick en el que se produce el cambio*/
  int   n_notas;           /* numero de notas de la pista (lo tengo en cabecera) */	
  int   n_msgModulacion; /* numero de mensajes de modulaci�n */
  int   n_msgAltura;   /* numero de msgs de cambio de altura */
  int   n_msgPostPul;  /* numero de msgs de postpulsaci�n    */
  int   maxPolyphony; /* maximo numero de notas simultaneas */
  float avgPolyphony; /* porcentaje de notas simultaneas */
} TDescriptoresPista;

/***************************************************************************

Estructura: TDescriptoresMidi
Almacena los descriptores de una pista
***************************************************************************/

typedef struct {
  char *path;
  long int bytes;
  int formato;
  int division; /* pulsos por nota negra*/
  int numpistas;
  char* texto;
  float tempo;
  int num_compas; /*numerador del compas*/
  int den_compas;  /*denominador del compas*/
  char *compases;
  int tono;
  int modo;  
  char* key;
  int c_tempo;
  int c_metrica;
  int c_tono;
  int duracion;
  int hasSysEx;
  char* instrumentos;
  char* percusion;
} TDescriptoresMidi;




/***************************************************************************

Estructura: TPista
Estructura en que represebta una pista MIDI, se compone de 
TCabeceraPista y un array de TEvento's. 
***************************************************************************/


typedef struct {

   TCabeceraPista     cabecera; 
   TEvento            *evento; /* los eventos tal cual leidos del midi */
   TNota	      *nota; /* de los eventos nos quedamos nada m�s con las notas*/
   TDescriptoresPista descriptores;
   	   
} TPista;


/***************************************************************************

Estructura: TMidi
Representa un archivo MIDI, se compone de TCabeceraMidi y un array de 
TPista's (de momento estatico).
***************************************************************************/


typedef struct {

   TCabeceraMidi     cabecera;
   TDescriptoresMidi descriptores;
   TPista            pistas[64]; 	
   
} TMidi;


int streq(char *a,char *b);
char* limpiarComillas(char *s);
char *concat(char *s1, char *s2, ...);
TNota* AnalizaNotas(TEvento *Leventos, DATOS numeventos, DATOS *numnotas);
DATOS NotaBaja(TNota *notas,int numnotas);
DATOS NotaAlta(TNota *notas,int numnotas);
float Media(TNota *notas,int numnotas);
float Desviacion(TNota *notas,int numnotas,float media);
int DuracionPista(TNota *notas,TEvento *eventos,int numnotas,int numeventos);
int DuracionPistaMasLarga(TMidi midi);
int DuracionCancion(TMidi midi);
unsigned long int NotasSolapadas(TNota *notas,int numnotas);
float EsPolifonica(TNota *notas,int numnotas);
int OcupacionPista(TNota *notas,int numnotas);
int Canal(TEvento *eventos,int numeventos);
int SecuenciaMasLargaQue(TNota *notas,int numnotas,int min);
void CuentaMsg(TEvento *eventos,int numeventos,int *n_cambiosPrograma, int *n_msgModulacion, int *n_msgAltura, int *n_msgPost);
void CuentaCambiosPrograma(TEvento *eventos, int numeventos, TDescriptoresPista *tdp);
char* ConcatenaTexto(TEvento *eventos,int numeventos);
void CargaDescriptoresPista(TMidi midi,int n,TDescriptoresPista *valor,int duracionPistaMasLarga, int duracionCancion);
int Tipo(TMidi midi);
int tieneSysEx(TMidi midi);
char* Instrumentos(TMidi midi);
char* Percusion(TMidi midi);
int Division(TMidi midi);
int NumPistas(TMidi midi);
void Tempo(TMidi midi, float *tempo, int *c_tempo);
char* Compas(TMidi midi,int *numerador,int *denominador, int *c_compas);
//void Tonalidad(TMidi midi,int *tono,int *modo);
//char* Tonalidad(TMidi midi, int *tono, int *modo);
char* Tonalidad(TMidi midi, int *tono, int *modo, int *cKey);
void CargaDescriptoresMidi(TMidi midi,TDescriptoresMidi *valor);
//TMidi CargaMidi(char *ruta,int *vale);
void CargaMidi(TMidi *midi, char *ruta, int *vale);
//void EscribeLin(TMidi midi, char *nombre, FILE *fich);
int maxPolyphony(TMidi midi, int nPista);
double avgPolyphony(TMidi midi, int nPista, int ocupacion);
double polyphonyRate(TMidi midi, int nPista, int ocupacion);


#endif /*TMIDI_H_*/



