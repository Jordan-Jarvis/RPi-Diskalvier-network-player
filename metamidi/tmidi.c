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

 Libreria MIDI
 Fichero tmidi.c
 Funciones de la libreria cuya finalidad es la de servir para trabajar con los
 archivos MIDI de forma m�s comoda, cada una de las funciones vendra precedida 
 de una explicaci�n de que es y para que sireve.
  
*****************************************************************************/

#include <unistd.h>
#include <stdio.h>
#include <math.h>
#include <string.h>
#include <stdarg.h>
#include <stdlib.h>
#include <sys/stat.h>
#include <sys/types.h>
#include "tmidi.h"
#include "define.h"

/****************************************************************************

Funciones auxiliares

****************************************************************************/


/* ----- Calcula el tiempo delta (n�mero de pulsos seg�n resoluci�n) ---- */
int Calc_tdelta ( DATOS8 *data, int *i )
{
    int t_delta = 0;

    while ( data[*i]>0x7F ) {
      t_delta = t_delta*128 + (data[*i]%128); *i+=1;
    }
    t_delta = t_delta*128 + data[*i];
    *i+=1;
    return t_delta;
}


/*----------------------------------------------------------*/
/*
	Funcion: streq
	Descripcion: devuelve 0 si las cadenas son distintas y otro
		valor en caso contrario.
	Argumentos: las dos cadenas a comparar.
	Observaciones: no da errores en caso de que alguna de los
		argumentos sea NULL.
*/

int streq(char *a,char *b)
{
	if(a)
		if(b)
			return(0==strcmp(a,b));
		else
			return 0;
	else
		return 0;
}

char* limpiarComillas(char *s)
{
	int i, j, l;
	char *aux;

	
	if (s != NULL)
	{
		l = strlen(s)+10;
		aux = (char*)malloc(l*sizeof(char));
		strcpy(aux, s);
		
		//limpiar comillas
		l = strlen(aux);
		for(i=0; i<l; i++)
		{
			if(aux[i] == '"')
			{
				aux[i] = '\'';
			}
		}
		
		//limpiar &
		l = strlen(aux);
		for(i=0; i<l; i++)
		{
			if(aux[i] == '&')
			{
				if(aux[i+1] != 'a' || aux[i+2] != 'm' || aux[i+3] != 'p' || aux[i+4] != ';')
				{
					aux = (char*)realloc((char*)aux, (l+4)*sizeof(char));
					
					for(j=l; j>i; j--)
					{
						aux[j+4] = aux[j];
					}

					aux[i] = '&';
					aux[i+1] = 'a';
					aux[i+2] = 'm';
					aux[i+3] = 'p';
					aux[i+4] = ';';

					l=l+4;
				}
			}
		}
		
		//limpiar <
		l = strlen(aux);
		for(i=0; i<l; i++)
		{
			if(aux[i] == '<')
			{
				aux = (char*)realloc((char*)aux, (l+3)*sizeof(char));
					
				for(j=l; j>i; j--)
				{
					aux[j+3] = aux[j];
				}
	
				aux[i] = '&';
				aux[i+1] = 'l';
				aux[i+2] = 't';
				aux[i+3] = ';';
				
				l=l+3;
			}
		}
		
		//limpiar >
		l = strlen(aux);
		for(i=0; i<l; i++)
		{
			if(aux[i] == '>')
			{
				
				aux = (char*)realloc((char*)aux, (l+3)*sizeof(char));

				for(j=l; j>i; j--)
				{
					aux[j+3] = aux[j];
				}
	
				aux[i] = '&';
				aux[i+1] = 'g';
				aux[i+2] = 't';
				aux[i+3] = ';';
				
				l = l+3;
			}
		}

		//filtar los caracteres validos entre los ASCII 32 y 126
		l = strlen(aux);
		for(i=0; i<l-1; i++)
		{
			if((int)aux[i] < 32 || (int)aux[i]>126)
			{
				aux[i] = ' ';
			}
		}
	}
	
	return aux;
}

/*-----------------------------------------------------------*/
/*	
	Funcion: concat
	Descripcion: concatena un numero variable de cadenas.
	Argumentos: cadenas a concatenar y la ultima cEOA
		s=concat(s1,s2,...,cEOA);
	Observaciones:
		- No da errores si alguna de las cadenas es NULL.
		- Libera la memoria eficientemente, no dejando residuos
*/

char *concat(char *s1, char *s2, ...)
{
	va_list ap;
	int l1=(s1?strlen(s1):0), l2=(s2?strlen(s2):0); 
	int cr, ca, la, ls;
	char *sa, *ss, *saux;

	sa=(char*)malloc((l1+l2+1)*sizeof(char));
	for(cr=0; cr<l1; cr++)
	{
		sa[cr]=s1[cr];
	}
	for(ca=0; ca<l2; sa[cr++]=s2[ca++]);
	va_start(ap, s2);
	for(la=l1+l2,ss=va_arg(ap,char*);!streq(ss,cEOA);ss=va_arg(ap,char*)) 
	{
		// longitud de la siguiente cadena a concatenar
		ls=(ss?strlen(ss):0);
		// reservamos memoria para la cadena acumulada mas la siguiente
		saux=(char *)malloc((la+ls+1)*sizeof(char));
		// copiamos ambas en la cadena auxiliar
		for(cr=0; cr<la; cr++)
		{
			saux[cr]=sa[cr];
		}
		for(ca=0;ca<ls;saux[cr++]=ss[ca++]);
		// liberamos memoria de la antigua sa
		free(sa);
		// actualizamos puntero a nueva sa y longitud acumulada
		sa=saux;
		la+=ls;
	}
	va_end(ap);
	sa[la]='\0';
	return sa;
}

/*----------------------------------------------------------*/

/*-----------------------------------------------------------
	Funcion: GetFicheros
	Descripicion: Nos devuelve los ficheros de una ruta que cumplan
		      cierta condicion
	Entrada: ruta, filtro
	Salida : array con las rutas de los ficheros,numero de ficheros
-----------------------------------------------------------*/



/****************************************************************************

Fin Funciones auxiliares

****************************************************************************/




/****************************************************************************

Funcion: AnalizaNotas.
Argumentos: Eventos de una pista
Devuelve: Notas de esa pista

****************************************************************************/

TNota*
AnalizaNotas(TEvento *Leventos, DATOS numeventos, DATOS *numnotas){
	int i,j,n,evento;
	TNota *temp,*notas;
	int ya = FALSO;
	DATOS nota_actual; /*la nota acttual*/
	int inicio,duracion,velocidad,ligada,compas;
	compas = -1;
	notas = temp = NULL;
	n = 0; /* nota actual */
	for(evento=0;evento<numeventos;evento++){
		/*buscamos NOTE_ON*/
		i = evento;
		if (Leventos[i].tipo == CANAL && Leventos[i].mensaje ==  NOTA_ON && Leventos[i].dato2 !=0){
			/* buscamos el fin de nota NOTA_OFF o NOTA_ON v == 0*/
			ya = FALSO;
			nota_actual = Leventos[i].dato1;
			for(j=i+1;(j<numeventos && ya == FALSO);j++)
			{
			    if ( (Leventos[j].mensaje == NOTA_OFF && Leventos[j].dato1 == nota_actual) || 
			    	 (Leventos[j].mensaje == NOTA_ON  && Leventos[j].dato1 == nota_actual && Leventos[j].dato2 == 0)
			       ){
			       	/* hemos encontrado el final de nota la guardamos */
			    	ya = CIERTO;
			    	inicio = Leventos[i].tini;
			    	duracion = Leventos[j].tini - inicio;
			    	velocidad = Leventos[i].dato2;
			    	ligada = FALSO;
			    	if(n==0)
			    		notas = (TNota*)malloc((n+1)*sizeof(TNota));
			    	else
			    		notas = (TNota*)realloc(notas,(n+1)*sizeof(TNota));
					notas[n].nota      = nota_actual;
					notas[n].velocidad = velocidad;
					notas[n].inicio    = inicio;
					notas[n].duracion  = duracion;
					notas[n].ligada    = ligada;
					notas[n].compas    = compas;
	                n++;
			    }
			    else
			    {
			    	
			    	/*vemos si ha llegado el final... si es as� la nota no se ha 'parado'
			    	  suponemos que termina al final del MIDI */
			    	if (j>=numeventos)
			    	{
			    		ya  = CIERTO;
			    		//printf("la nota : %d\n",nota_actual);
			    		inicio = Leventos[i].tini;
				       	duracion = Leventos[numeventos-1].tini - inicio;
				       	velocidad = Leventos[i].dato2;
				       	ligada = FALSO;
				       	
				       	if(n==0)
				       		notas = (TNota*)malloc((n+1)*sizeof(TNota));
				       	else
				       		notas = (TNota*)realloc(notas,(n+1)*sizeof(TNota));
				       	notas[n].nota     = nota_actual;
				       	notas[n].velocidad = velocidad;
				       	notas[n].inicio   = inicio;
				       	notas[n].duracion = duracion;
				       	notas[n].ligada   = ligada;
				       	notas[n].compas   = compas;
				       	n++;	
	                }       
			    }   		 
			}
			/*fin for busca fin nota*/				
		}/*fin del if*/
	}	
	*numnotas = n;
	if (notas == NULL){
		notas = (TNota*)malloc(1*sizeof(TNota));
		notas[0].nota = -1;
	}
return notas;
}
/* fin funcion AnalizaNotas()*/



/****************************************************************************

Funcion: NotaBaja().
Argumentos: Notas de una pista, numero de notas
Devuelve: La Nota mas baja de una pista

****************************************************************************/

DATOS
NotaBaja(TNota *notas,int numnotas){
int i,min;
	if (numnotas > 0){
		min = notas[0].nota;
			for(i=0;i<numnotas;i++){
				if (notas[i].nota < min)
					min = notas[i].nota;		
			}
	}	 
	else
		return -1;	
return min;
}
/****************************************************************************

Funcion: NotaAlta().
Argumentos: Notas de una pista, numero de notas
Devuelve: La Nota mas alta de una pista

****************************************************************************/

DATOS
NotaAlta(TNota *notas,int numnotas){
int i,max;
	if (numnotas > 0){
		max = notas[0].nota;
			for(i=1;i<numnotas;i++){
				if (notas[i].nota > max)
					max = notas[i].nota;		
			}
	}	 
	else
		return -1;	
return max;
}


/****************************************************************************

Funcion: Media().
Argumentos: Notas de una pista, numero de notas
Devuelve: La media de la pista

****************************************************************************/

float
Media(TNota *notas,int numnotas){
int i;
int tot;
float media;
tot = 0;
	if (numnotas > 0){
		for(i=0;i<numnotas;i++){
			tot = tot + notas[i].nota;	
		}
	media = (float) tot / numnotas;
	return media;
	}
	else{
		return -1;
	}
}


/****************************************************************************

Funcion: Desviacion().
Argumentos: Notas de una pista, numero de notas, media
Devuelve: La desviacion de la pista

****************************************************************************/


float
Desviacion(TNota *notas,int numnotas,float media){
int i;
float desv;
int sum=0;
	if (numnotas > 0){
		for(i=0;i<numnotas;i++){
			sum = sum + abs(notas[i].nota - media);			
		}	
	desv = (float) sum / numnotas;
	return desv;
	}
	else{
		return -1;
	}
}




/****************************************************************************

Funcion: DuracionPista().
Argumentos: Notas de una pista, numero de notas, numero de eventos
Devuelve: duracion de la pista

****************************************************************************/

int
DuracionPista(TNota *notas,TEvento *eventos,int numnotas,int numeventos){
	int durN,durE;
	int fin, i;
	
	durN = durE = -1;
	if (numnotas > 0) {
		
		if(notas[0].nota !=-1)
		{
			fin = notas[0].inicio + notas[0].duracion;
			
			for(i=1;i<numnotas;i++)
			{
				if((notas[i].inicio + notas[i].duracion) > fin)
				{
					fin = notas[i].inicio + notas[i].duracion;
				}
			}
			durN = fin - notas[0].inicio;
		}
		
		//durN = notas[numnotas-1].inicio + notas[numnotas-1].duracion;
		//durN = notas[numnotas-1].inicio + notas[numnotas-1].duracion - notas[0].inicio;
	}
	if (numeventos > 0){
		//durE = eventos[numeventos-1].tini;
		durE = eventos[numeventos-1].tini - eventos[0].tini;
	}
	
	if(durN > durE)
		return durN;
	else
		return durE;
}

int
DuracionPistaMasLarga(TMidi midi){
int i,max,dur;
max = 0;

//	for(i=0;i<midi.cabecera.numpistas;i++){
	for(i=0;i<midi.cabecera.numpistas;i++){
		dur = DuracionPista(midi.pistas[i].nota,midi.pistas[i].evento,midi.pistas[i].cabecera.numnotas,midi.pistas[i].cabecera.numeventos);
		if (dur > max){
			max = dur; 	
		}
	}
	//printf(" %d ", max);
return max;
}

int
DuracionCancion(TMidi midi)
{
	int i, max, dur, ultimanota, ultimoevento;
	
	max = 0;
	for(i=0;i<midi.cabecera.numpistas;i++)
	{
		if(midi.pistas[i].cabecera.numnotas > 0)
		{
			ultimanota = midi.pistas[i].cabecera.numnotas-1;
			
			dur = midi.pistas[i].nota[ultimanota].inicio + midi.pistas[i].nota[ultimanota].duracion; 
		}
		else
		{
			dur = 0;
		}
		
		//printf("************************************ max nota: %d, pista: %d\n", dur, i);
		if(dur > max)
		{
			max = dur;			
		}
	}
	//printf("************************************ max nota: %d\n", max);
	
	
	for(i=1;i<midi.cabecera.numpistas;i++)
	{
		if(midi.pistas[i].cabecera.numeventos > 0)
		{
			ultimoevento = midi.pistas[i].cabecera.numeventos-1;
			
			dur = midi.pistas[i].evento[ultimoevento].tini; 
		}
		else
		{
			dur = 0;
		}
		
		if(dur > max)
		{
			max = dur;			
		}
	}
	
	//printf("************************************ max evento: %d\n", max);
	
	return max;
}


/****************************************************************************

Funcion: NotasSolapadas().
Argumentos: Notas de una pista, numero de notas 
Devuelve: 'tiempo'  polifonico de la pista

****************************************************************************/



unsigned long int
NotasSolapadas(TNota *notas,int numnotas){
int i;
unsigned long int t_acumulado;
int fin_polifonia,inicio_polifonia;
t_acumulado = 0;
i=0;
inicio_polifonia = notas[i].inicio;
fin_polifonia = notas[i].inicio + notas[i].duracion;
	while (i<numnotas-1){
		i++;
		if (notas[i].inicio < fin_polifonia){ /* hay solapamiento */
			if ( (notas[i].inicio + notas[i].duracion) < fin_polifonia){
				if (notas[i].inicio < inicio_polifonia){
					t_acumulado += notas[i].inicio + notas[i].duracion  - inicio_polifonia;
				}
				else{
					t_acumulado += notas[i].duracion;
				}
			 	inicio_polifonia = notas[i].inicio + notas[i].duracion;
			 	fin_polifonia = notas[i].inicio + notas[i].duracion;
			}
			else{
				if (notas[i].inicio < inicio_polifonia){
					t_acumulado += fin_polifonia - inicio_polifonia;
				}
				else{
					t_acumulado += fin_polifonia - notas[i].inicio;
 				}
			 	inicio_polifonia = fin_polifonia;
			 	fin_polifonia = notas[i].inicio + notas[i].duracion;
								
			}
		}
		else{ /* no hay solapamiento */
			inicio_polifonia = notas[i].inicio;
			fin_polifonia = notas[i].inicio + notas[i].duracion;
		}
	}
return t_acumulado;
}

/****************************************************************************

Funcion: EsPolifonica().
Argumentos: Notas de una pista, numero de notas 
Devuelve: El tanto por 1 de tiempo polifonico de la pista

****************************************************************************/

float
EsPolifonica(TNota *notas,int numnotas){
int t_polifonico,duracion;
float valor;
duracion = DuracionPista(notas,NULL,numnotas,-1); 
t_polifonico = NotasSolapadas(notas,numnotas);
if (duracion != -1)
	valor = (float) t_polifonico / duracion;
else
	valor = -1;
return valor;
}


/****************************************************************************

Funcion: OcupacionPista().
Argumentos: Notas de una pista, numero de notas 
Devuelve: El tiempo durante el que suena alguna nota en la pista.

****************************************************************************/

int
OcupacionPista(TNota *notas,int numnotas){
/* calculamos el tiempo que no suena nada y se lo restamos a la duracion de la pista*/
	int t_acumulado,duracion;
	int fin,i;
	
	//printf("******************\n");

	
	if (notas[0].nota !=-1){
		fin = notas[0].inicio + notas[0].duracion;
		t_acumulado = 0;
		
		//printf("inicio: %d, duracion: %d\n", notas[0].inicio, notas[0].duracion);
		
		for(i=1;i<numnotas;i++){
			//printf("inicio: %d, duracion: %d\n", notas[i].inicio, notas[i].duracion);

			if(notas[i].inicio > fin){
				//t_acumulado = t_acumulado + notas[i].inicio - fin;
				t_acumulado = t_acumulado + (notas[i].inicio - fin);
			}
			if((notas[i].inicio + notas[i].duracion) > fin) {
				fin = notas[i].inicio + notas[i].duracion;
			}
		}
		duracion = DuracionPista(notas,NULL,numnotas,-1);
		if (fin < duracion)
			t_acumulado += (duracion - fin);
		
		return  (duracion - t_acumulado);
		
	}
	else{
		//return -1;
		return 0;
	}	 
}

/****************************************************************************

Funcion: Canal().
Argumentos: Eventos de una pista, numero eventos
Devuelve: El canal sobre el que actua la pista (el primero que encuentra)

****************************************************************************/


int
Canal(TEvento *eventos,int numeventos){
int i,canal;
canal = -1;
	for(i=0;i<numeventos;i++){
	 if (eventos[i].tipo == CANAL && eventos[i].canal != canal){
		canal = eventos[i].canal;
		return canal;	  				
	    }
	}
return canal;
}










/***************************************************************************

Funciones 'experimento' busca la secuencia de notas que mas se repite (con un 
minimo de notas) y la secuencia de notas m�s larga que se repite al menos n veces)


***************************************************************************/











/***************************************************************************

Funcion: SecuenciaMasLargaQue
Argumentos: notas de una pista, numero de notas, minimo tamanyo de secuencia
Devuelve: Longitud de la secuencia que m�s se repite (de m�s de un tamanyo minimo)
la secuencia se calcula mirando los intervalos y no las notas
***************************************************************************/



int
SecuenciaMasLargaQue(TNota *notas,int numnotas,int min){
int i,j,k,l,sigue;
int n_max,n_act;
int *act;
n_max = -1;
n_act = -1;
act =(int*)malloc((min-1)*sizeof(int));

	for(i=0;i<numnotas-min-1;i++){
		n_act = -1;
		sigue = CIERTO;
		k=0;
		j = i;
		for(j=j;j<i+min-1;j++){
			act[k] = notas[j+1].nota - notas[j].nota;	
			k++;
		}
		/*vemos si el siguiente coincide*/
		j++;
		for(j=j;j<numnotas;j++){	
		k=0;
		l=j;	
		sigue = CIERTO;
			while (sigue == CIERTO && l < j+min-1){
				if(act[k] != notas[l+1].nota - notas[l].nota){
					sigue = FALSO;
				}
			k++;
			l++;
			}
			if (sigue == CIERTO){
			n_act ++;
			}			
		}
	
		if (n_act > n_max){
			n_max = n_act + 2;
		}
	}
return n_max;
}

/***************************************************************************

Funcion: CuentaMsg(TEvento *eventos,int numeventos,int *n_cambiosPrograma, int *n_msgModulacion, int *n_msgAltura, int *n_msgPost)
Argumentos: Estructura TEvento, numero de eventos
Devuelve: Numero de mensajes de cambio de tempo

***************************************************************************/
void
CuentaMsg(TEvento *eventos,int numeventos,int *n_cambiosPrograma, int *n_msgModulacion, int *n_msgAltura, int *n_msgPost){
	int i;
	*n_cambiosPrograma = 0;
	*n_msgModulacion = 0;
	*n_msgAltura = 0;
	*n_msgPost = 0;
	for(i=0;i<numeventos;i++){
		/*if (eventos[i].mensaje == C_PROGRAMA)
			*n_cambiosPrograma = *n_cambiosPrograma+1;
		else*/ 
		if(eventos[i].mensaje == MODULACION)
			*n_msgModulacion = *n_msgModulacion+1;
		else if(eventos[i].mensaje == ALTURA)
			*n_msgAltura= *n_msgAltura+1;
		else if(eventos[i].mensaje == POST_CANAL || eventos[i].mensaje == POST_POLIF)
			*n_msgPost= *n_msgPost+1;
	}
}	


void 
CuentaCambiosPrograma(TEvento *eventos, int numeventos, TDescriptoresPista *tdp)
{
	int i;
	char *aux;
	
	tdp->n_cambiosPrograma = 0;
	tdp->cambiosPrograma = strdup("$");
	
	
	//printf("-------------------numero eventos: %d\n", numeventos);

	aux = (char*)malloc(sizeof(int)*20);

	
	for(i=0;i<numeventos;i++)
	{
		//printf("-------------------evento: %d\n", eventos[i].mensaje);

		//if(eventos[i].mensaje == C_PROGRAMA)
		if (eventos[i].mensaje == C_PROGRAMA && eventos[i].canal != 10)
		{

			if(tdp->n_cambiosPrograma == 0)
			{
				tdp->cambiosPrograma = strdup("");
			}
			else
			{
				tdp->cambiosPrograma = concat(tdp->cambiosPrograma, ",", cEOA);
			}
			
			//sprintf(aux, "%d", eventos[i].dato1);
			sprintf(aux, "%d", eventos[i].dato1+1);
			tdp->cambiosPrograma = concat(tdp->cambiosPrograma, aux,cEOA);
			
			sprintf(aux, "(%d)", eventos[i].tini);
			tdp->cambiosPrograma = concat(tdp->cambiosPrograma, aux,cEOA);
			
			tdp->n_cambiosPrograma++;
		}
	}
	
	free(aux);
}

/***************************************************************************

Funcion: ConcatenaTexto(TEvento *eventos,int numeventos)
Argumentos: Estructura TEvento, numero de eventos
Devuelve: los metatextos concatenados separados por coma

***************************************************************************/
	

char*
ConcatenaTexto(TEvento *eventos,int numeventos){
	int i;
	char *texto;
	
	texto = strdup("");
	
	for(i=0;i<numeventos;i++)
	{
		if (eventos[i].mensaje == TEXTO 
				|| eventos[i].mensaje == COPYRIGTH 
				|| eventos[i].mensaje == NOM_PISTA 
				|| eventos[i].mensaje == NOM_INST
				|| eventos[i].mensaje == LETRA)
		{
			if (strcmp(texto, "") == 0)
			{
				if(strcmp(eventos[i].texto,"") != 0)
					texto = strdup(eventos[i].texto);
				else
					texto = strdup("$");
				
			}
			else
			{
				if(strcmp(eventos[i].texto,"") != 0)
					texto = concat(texto,",",eventos[i].texto,cEOA);
				else
					texto = concat(texto,",$,",cEOA);
		
			}
			
			//printf("%d | %s\n", eventos[i].tini, eventos[i].texto);
		}
	}
	
	/* quitamos los \n y ponemos ' '*/
	for(i=0;i<strlen(texto);i++)
	{
		if (texto[i] == '\n')
		{
			texto[i] = ' ';
		}
	}
	
	return texto;
}

	




/***************************************************************************

Funcion: CargaDescriptotesPista(TMidi midi,int numpista)
Argumentos: Estructura Midi,numero de pistas
Devuelve: Los descriptores de la pista 'numpista' del fichero 'midi'

***************************************************************************/


void
CargaDescriptoresPista(TMidi midi,int n,TDescriptoresPista *valor,int duracionPistaMasLarga, int duracionCancion){

	char *aux;
	
	valor->nota_baja  = NotaBaja(midi.pistas[n].nota,midi.pistas[n].cabecera.numnotas);
	valor->nota_alta  = NotaAlta(midi.pistas[n].nota,midi.pistas[n].cabecera.numnotas);
	valor->duracion   = DuracionPista(midi.pistas[n].nota,midi.pistas[n].evento,midi.pistas[n].cabecera.numnotas,midi.pistas[n].cabecera.numeventos);
	valor->canal      = Canal(midi.pistas[n].evento,midi.pistas[n].cabecera.numeventos);
	valor->d_sonido   = OcupacionPista(midi.pistas[n].nota,midi.pistas[n].cabecera.numnotas);
	//valor->polifonica = EsPolifonica(midi.pistas[n].nota,midi.pistas[n].cabecera.numnotas);
	valor->polifonica = polyphonyRate(midi, n, valor->d_sonido);
	
	//printf("ocuapacion de la pista: %d\n", valor->d_sonido);
	
	if(valor->duracion == 0)
	{
		valor->sonido = 0;
	}
	else
	{
		valor->sonido     = (float) valor->d_sonido / valor->duracion;
	}
	
	valor->media      = Media(midi.pistas[n].nota,midi.pistas[n].cabecera.numnotas);
	valor->desviacion = Desviacion(midi.pistas[n].nota,midi.pistas[n].cabecera.numnotas,valor->media);

	valor->d_absoluta = (float) valor->duracion / duracionCancion;
	
	if(duracionPistaMasLarga > 0)
	{
		//valor->d_absoluta = (float) valor->duracion / duracionPistaMasLarga;
		valor->s_absoluto = (float) valor->d_sonido / duracionPistaMasLarga; 
	}
	else
	{
		valor->d_absoluta = -1;
		valor->s_absoluto = -1; 
	}
	
	CuentaMsg(midi.pistas[n].evento,midi.pistas[n].cabecera.numeventos,&valor->n_cambiosPrograma,&valor->n_msgModulacion,&valor->n_msgAltura,&valor->n_msgPostPul);
	CuentaCambiosPrograma(midi.pistas[n].evento, midi.pistas[n].cabecera.numeventos, valor);
		
	aux = ConcatenaTexto(midi.pistas[n].evento,midi.pistas[n].cabecera.numeventos);
	if(strcmp(aux, "") == 0)
		valor->texto = strdup("$");
	else
		valor->texto = strdup(aux);
	
	valor->maxPolyphony = maxPolyphony(midi, n);
	//printf("ocuapacion de la pista: %d\n", valor->d_sonido);
	valor->avgPolyphony = avgPolyphony(midi, n, valor->d_sonido);
	
}

/**************************************************************************/
/* FUNCIONES PARA CALCULAR LOS DESCRIPTORES DEL MIDI                      */ 
/**************************************************************************/

int
tieneSysEx(TMidi midi)
{
	int i,j;
	int dev;
	
	dev=0;
	for(i=0;i<midi.cabecera.numpistas;i++)
	{
		for(j=0;j<midi.pistas[i].cabecera.numeventos;j++)
		{
			if(midi.pistas[i].evento[j].mensaje == SISEX)
			{
				dev=1;
				//para salir del bucle
				i = midi.cabecera.numpistas;
				j = midi.pistas[i].cabecera.numeventos;
			}
			
			//printf("mensaje: %d\n",midi.pistas[i].evento[j].mensaje);
		}
	}

	return dev;
}

char*
Instrumentos(TMidi midi)
{
	int i,j,k,ordenar;
	char *dev, *aux;
	int longDev;
	int *vTemporal;
	int nTemporal;
	int nCambiosPista; //numero de cambios que se realizan en una pista
	
	dev = (char*)malloc(sizeof(char)*2);
	dev[0]='\0';

	aux = (char*)malloc(sizeof(char)*20);

	//printf("Instrumentos: \n");

	
	//printf("numpistas: %d\n", midi.cabecera.numpistas);

	nTemporal = 0;
	for(i=0;i<midi.cabecera.numpistas;i++)
	{
		nCambiosPista = 0;
		for(j=0;j<midi.pistas[i].cabecera.numeventos;j++)
		{
			//if(midi.pistas[i].evento[j].mensaje == C_PROGRAMA)
			//cambios de programa de los canales que no sean de percusion (canal10)
			if(midi.pistas[i].evento[j].mensaje == C_PROGRAMA && midi.pistas[i].evento[j].canal != 10)
			{
				
				nCambiosPista++;
				//printf("*-*-*-*-*-*-*-*-*-*-*-programa*-*-*-*-*-*-*-*-*-*-*-*-*-\n");
				//tamaño del vector temporal
				if(nTemporal == 0)
				{
					nTemporal++;
					vTemporal = (int*)malloc(sizeof(int)*nTemporal);
				}
				else
				{
					nTemporal++;
					vTemporal = (int*)realloc(vTemporal, sizeof(int)*nTemporal);
				}

				vTemporal[nTemporal-1] = midi.pistas[i].evento[j].dato1+1;
			}
		}
		
		//si en la pista no se ha realizado ningún cambio de programa se pone 0
		if(nCambiosPista == 0)
		{
			if(nTemporal == 0)
			{
				nTemporal++;
				vTemporal = (int*)malloc(sizeof(int)*nTemporal);
			}
			else
			{
				nTemporal++;
				vTemporal = (int*)realloc(vTemporal, sizeof(int)*nTemporal);
			}

			vTemporal[nTemporal-1] = -1;
		}
	}

	//ordenar vector
	for(i=0; i<nTemporal; i++)
	{
		k=i;
		for(j=i; j< nTemporal; j++)
		{
			if(vTemporal[j] < vTemporal[k])
			{
				k = j;
			}
		}
		if(k != i)
		{
			ordenar = vTemporal[i];
			vTemporal[i] = vTemporal[k];
			vTemporal[k] = ordenar;
		}
	}
	
	//quitar duplicados y valores no validos
	i=0;
	while(i<nTemporal-1)
	{
		if(vTemporal[i] == vTemporal[i+1] || vTemporal[i] < 1 || vTemporal[i] > 128)
		{
			for(j=i; j<nTemporal-1; j++)
			{
				vTemporal[j] = vTemporal[j+1];
			}
			
			nTemporal--;
		}
		else
		{
			i++;
		}
	}
	
	//almacenar en el array
	for(i=0; i < nTemporal; i++)
	{	
		sprintf(aux, "%d,", vTemporal[i]);
		dev = (char*)realloc(dev, sizeof(char)*(strlen(dev) + strlen(aux) + 20));
		strcat(dev, aux);
	}

	
	longDev = strlen(dev);
	
	//quitar la ultima coma
	if(longDev > 0)
	{
		dev[longDev-1] = '\0';
	}
	
	
	free(aux);

	return dev;
}

char*
Percusion(TMidi midi)
{
	int i,j,k;
	char *dev;
	int bateria, latin, otro;
	int longDev;
		
	dev = (char*)malloc(sizeof(char)*20);
	dev[0]='\0';


	//printf("Instrumentos: \n");

	
	//printf("numpistas: %d\n", midi.cabecera.numpistas);

	bateria=latin=otro=0;
	dev[0]='\0';
	
	for(i=0;i<midi.cabecera.numpistas;i++)
	{
		for(j=0;j<midi.pistas[i].cabecera.numeventos;j++)
		{
			//buscar pista de canal 10
			if(midi.pistas[i].evento[j].canal == 10)
			{
				for(k=0; k<midi.pistas[i].cabecera.numnotas; k++)
				{
					//printf("*-*-*-*-*-*-*-*-*-*-*-programa*-*-*-*-*-*-*-*-*-*-*-*-*-\n");

					switch(midi.pistas[i].nota[k].nota)
					{
					case 35:
					case 36:
					case 37:
					case 38:
					case 40:
					case 41:
					case 42:
					case 43:
					case 44:
					case 45:
					case 46:
					case 47:
					case 48:
					case 49:
					case 50:
					case 51:
					case 52:
					case 53:
					case 55:
					case 57:
					case 59:
						//bateria
						bateria = 1;
						break;
					case 60:
					case 61:
					case 62:
					case 63:
					case 64:
					case 65:
					case 66:
					case 67:
					case 68:
					case 69:
					case 70:
					case 71:
					case 72:
					case 73:
					case 74:
					case 75:
					case 78:
					case 79:
					case 82:
					case 86:
					case 87:
						//Latin
						latin = 1;
						break;
					default:
						//otro
						otro = 1;
						break;
					}
				}
			}
		}
	}
	
	
	if(bateria == 1 || latin == 1 || otro == 1)
	{
		if(bateria == 1)
		{
			strcat(dev, "1,");
		}
				
		if(latin == 1)
		{
			strcat(dev, "2,");
		}

		if(otro == 1)
		{
			strcat(dev, "3,");
		}

		longDev = strlen(dev);
		
		//quitar la ultima coma
		if( longDev > 0)
		{
			dev[longDev-1] = '\0';
		}
	}
	else
	{
		strcat(dev, "-1");
	}
	
	return dev;
}



int
Tipo(TMidi midi){
	return midi.cabecera.format;
}

int
Division(TMidi midi){
	return midi.cabecera.delta;
}

int
NumPistas(TMidi midi){
	return midi.cabecera.numpistas;
}

void
Tempo(TMidi midi, float *tempo, int *c_tempo){
	int i,sigue;
	i=0;
	sigue = 0;
	
	/* buscamos el primer evento de tipo compas de la pista 0 del midi */

	*tempo = -1;
	*c_tempo = 0;
	while(i<midi.pistas[0].cabecera.numeventos)
	{
		if (midi.pistas[0].evento[i].mensaje == AJUS_TEMPO)
		{
			if(sigue == 0)
			{
				*tempo = midi.pistas[0].evento[i].dato3;
				sigue = 1;
				
			}
			
			//printf("%d ", midi.pistas[0].evento[i].tini);
			*c_tempo += 1;
		}
		i++;
	}
}

char*
Compas(TMidi midi,int *numerador,int *denominador, int *c_compas)
{
	int i,sigue;
	int num, dem, beat;
	char aux[100];
	char *compases;
	
	compases = (char*)malloc(sizeof(char)*2);
	compases[0] = '\0';
	aux[0] = '\0';
	
	*numerador = -1;
	*denominador = -1;
	*c_compas = 0;

	i=0;
	sigue = 0;
	while(i<midi.pistas[0].cabecera.numeventos)
	{
		if (midi.pistas[0].evento[i].mensaje == COMPAS)
		{
			num = midi.pistas[0].evento[i].dato1;
			dem = midi.pistas[0].evento[i].dato2;
			beat = midi.pistas[0].evento[i].tini;
			
			
			//solo la primera vez
			if(sigue == 0)
			{
				*numerador = num;
				*denominador = dem;
				sigue = 1;
			}

			sprintf(aux, "%d/%d(%d),", num, dem, beat);
			compases = concat(compases, aux, "", cEOA);
			
			//printf("%d ", midi.pistas[0].evento[i].tini);
			*c_compas +=1;
		}
		i++;
	}
	compases[strlen(compases)-1] = '\0';

	return compases;
}

char*
Tonalidad(TMidi midi, int *tono, int *modo, int *cKey)
{
	char  *tablatonalidad[] = {"CbM","GbM","DbM","AbM","EbM","BbM","FM","CM","GM","DM","AM","EM","BM","F#M","C#M",
							   "Abm","Ebm","Bbm","Fm","Cm","Gm","Dm","Am","Em","Bm","F#m","C#m","G#m","D#m","A#m"};
	int i, t, m;
	char *aux, *key;
	
	key = strdup("$");
	
	aux = (char*)malloc(sizeof(char)*50);

	*tono=-1;
	*modo=-1;

	
	*cKey = 0;
	for(i=0; i<midi.pistas[0].cabecera.numeventos; i++)
	{
		if (midi.pistas[0].evento[i].mensaje == TONALIDAD)
		{
						
			//salir del bucle

			
			if ( midi.pistas[0].evento[i].dato1 > 127 )
				t =  midi.pistas[0].evento[i].dato1-256;
			else 
				t =  midi.pistas[0].evento[i].dato1;

			m = midi.pistas[0].evento[i].dato2;

			if ( m ) 
				t = t+15;
			
			//printf("Key: %s",tono[indice+7]);
			
			
			//printf("********************************** %d\n", t);

			if((*cKey) == 0) 
			{
				*tono=t;
				*modo=m;

				free(key);
				key = strdup("");
			}			
			else
			{
				key = concat(key, "," ,cEOA);
			}
			
			sprintf(aux, "%d", midi.pistas[0].evento[i].tini);
			/*
			if(m)
			{
				//printf("t: %d, m: %d\n", t, m);
				key = concat(key, tablatonalidad[t], "(", aux, ")" , cEOA);
				//printf("Tonalidad, eventos: %d, t: %d, m: %d\n", midi.pistas[0].cabecera.numeventos, t, m);
			}
			else
			{
				key = concat(key, tablatonalidad[t], "(", aux, ")" , cEOA);
			}
			*/
			
			
			key = concat(key, tablatonalidad[t+7], "(", aux, ")" , cEOA);
			//printf("key: %s\n", key);
			//printf("tablatonalidad: %s ", tablatonalidad[t]);
			//printf("t: %d, m: %d \n", t, m);
			//printf("aux: %s\n", aux);

			(*cKey)++;
		}
	}
	
	free(aux);

	return key;
}


void
CargaDescriptoresMidi(TMidi midi,TDescriptoresMidi *valor){
	char *aux;
	struct stat results;
	
	valor->formato = Tipo(midi);
	valor->division = Division(midi);
	valor->numpistas = midi.cabecera.numpistas;
	
	Tempo(midi, &valor->tempo, &valor->c_tempo);
	valor->compases = Compas(midi,&valor->num_compas,&valor->den_compas, &valor->c_metrica);
	
	valor->key = Tonalidad(midi, &(valor->tono), &(valor->modo), &(valor->c_tono));
	
	aux = ConcatenaTexto(midi.pistas[0].evento, midi.pistas[0].cabecera.numeventos);

	if (strcmp(aux,"")== 0 )
		valor->texto = strdup("$");
	else
		valor->texto = strdup(aux);
		
	valor->path = midi.cabecera.name;
	//valor->duracion = DuracionPistaMasLarga(midi);
	valor->duracion = DuracionCancion(midi);

    if (stat(midi.cabecera.name, &results) == 0)
        // The size of the file in bytes is in
        valor->bytes = results.st_size;
    else
    	valor->bytes = 0;
    
    valor-> hasSysEx = tieneSysEx(midi);
    valor-> instrumentos = Instrumentos(midi);
    valor-> percusion = Percusion(midi);
}



/****************************************************************************

Funcion: CargaMidi.
Argumentos: ruta (la ruta del archivo a cargar.
Devuelve: TMidi (una estrcutura rellena con los datos del archivo).

****************************************************************************/

//TMidi
void
CargaMidi(TMidi *midi, char *ruta,int *vale){

	FILE *fin;
	int  i,j,npista;
	unsigned char aux;
	unsigned char status;
	float tempo;
	int n;
	char tmp[2];
	DATOS 	tipo;
	DATOS   mensaje;
	DATOS   dato1;
	DATOS   dato2;
	DOBLE   dato3;
	DATOS   canal;
	char*   texto;
	int     tini;
	int	t_delta;
	//int nTruco=0;
	//TMidi midi;
	
	char* path;

	*vale = 1;
	
	fin = fopen(ruta, "r");
	if(fin == NULL)
	{
		//printf("NULL");
		*vale = 0;
	    return;
	    //return midi;
	}
    
  //***********************************************
  //   Leemos los datos de la cabecera del archivo.  
  //***********************************************
	for (i=0; i<4; i++) 
	{
		midi->cabecera.id[i] = fgetc (fin);
	}
	midi->cabecera.id[4]='\0';

	if ( strcmp(midi->cabecera.id,"MThd") )
	{ 
		fprintf(stderr,"No es un fichero MIDI est�ndar\n"); 
		*vale = 0;
		//return midi;
		return;
	}
  
	midi->cabecera.size = 0;
	for (i=0; i<4; i++) 
	{
		aux = fgetc(fin);
		midi->cabecera.size = midi->cabecera.size * 256 + aux;
	}
  
	midi->cabecera.format = 0;
	for (i=0; i<2; i++) 
	{
		aux = fgetc(fin); 
		midi->cabecera.format = midi->cabecera.format * 256 + aux;
	}

	midi->cabecera.numpistas = 0;
	for (i=0; i<2; i++) 
	{
		aux = fgetc(fin); 
		midi->cabecera.numpistas = midi->cabecera.numpistas * 256 + aux;
	}
  
	midi->cabecera.delta = 0;
	for (i=0; i<2; i++) 
	{
		aux = fgetc(fin); 
		midi->cabecera.delta = midi->cabecera.delta * 256 + aux;
	}
  
	if(ruta[0] == '/') 
	{
		midi->cabecera.name = (char*)malloc(sizeof(char)*(strlen(ruta) + 20));
		strcat(midi->cabecera.name, ruta);
	}
	else
	{

		path = (char*)getcwd(NULL, 0);

		midi->cabecera.name = (char*)malloc(sizeof(char)*(strlen(path) + strlen(ruta) + 20));
		strcpy(midi->cabecera.name, path);
		strcat(midi->cabecera.name, "/");
		strcat(midi->cabecera.name, ruta);  
	  
		free(path);
	}
	  

  //***********************************************
  //   Leemos los datos de cada una de las 
  //   pistas del archivo.  
  //***********************************************
//  printf("\nHe leido la cabecera\n");

	for ( npista=0; npista<midi->cabecera.numpistas; npista++ )
	{

		// ---------------- CABECERA ------------------------ 
		midi->pistas[npista].evento=NULL;
		midi->pistas[npista].nota = NULL;
		//agrgamos la nueva pista
		for (i=0; i<4; i++) 
		{
			midi->pistas[npista].cabecera.id[i] = fgetc (fin);
		}	  
		midi->pistas[npista].cabecera.id[4]='\0';

		if ( strcmp(midi->pistas[npista].cabecera.id,"MTrk") ) 
		{
			fprintf(stderr,"No tiene la firma MTrk del bloque de datos (%s)\n"
			,midi->pistas[npista].cabecera.id); 
			*vale = 0;
			//return midi;
			return;
		}

		midi->pistas[npista].cabecera.size = 0;
		for (i=0; i<4; i++) 
		{
			aux = fgetc(fin); 
			midi->pistas[npista].cabecera.size = midi->pistas[npista].cabecera.size * 256 + aux;
		}

		midi->pistas[npista].cabecera.data = (DATOS8 *) malloc(2*midi->pistas[npista].cabecera.size * sizeof(DATOS8));
		fread(midi->pistas[npista].cabecera.data,sizeof(DATOS8),midi->pistas[npista].cabecera.size,fin);

		// -------------- ANALISIS DE LOS DATOS ----------------
		//   Anlizamos los datos de la pista y rellenamos el array 
		//   de eventos de la misma 
		//   ----------------------------------------------------
        tini = 0;
        tipo = -1;
        mensaje = -1;
        n = 0;
        i = -1;
        

        do 
        {
        	i++;
        	t_delta = Calc_tdelta(midi->pistas[npista].cabecera.data,&i);
        	canal = -1;
        	dato1 = -1;
        	dato2 = -1;
        	dato3 = -1;
        	texto = strdup("");
        	tini = tini + t_delta;
	    
        	if ( midi->pistas[npista].cabecera.data[i]==0xFF ) // Meta-evento
        	{ 
        		i++;
        		tipo = META;

        		switch ( midi->pistas[npista].cabecera.data[i] ) 
        		{
        			case 0x00 : // Numero de secuencia. 
        				//dato1 -> Numero de secuencia
        				//  	
        				mensaje = NUM_SEC;
        				dato1 = midi->pistas[npista].cabecera.data[i+2]*256 + midi->pistas[npista].cabecera.data[i+3];
        				i=i+4; 
        				break;
        			case 0x01 : // Texto 
        				//texto -> texto
				      

        				mensaje = TEXTO;			
        				i++;
        				for ( j=i+1; j<=i + midi->pistas[npista].cabecera.data[i]; j++ )
        				{
        					tmp[0] = midi->pistas[npista].cabecera.data[j];
        					tmp[1] = '\0';
        					texto = concat(texto,tmp,cEOA);
        				}	
        				
        				//printf("%s", texto);
        				
        				i=j-1;
        				break;
        			case 0x02 : // Copyrigth 
        				//texto -> Copyright
				      
        				mensaje = COPYRIGTH;		
        				i++;
        				for ( j=i+1; j<=i+midi->pistas[npista].cabecera.data[i]; j++ )
        				{
        					tmp[0] = midi->pistas[npista].cabecera.data[j];
        					tmp[1] = '\0';
        					texto = concat(texto,tmp,cEOA);
        				}	
        				i=j-1;
        				break;
        			case 0x03 : // Nombre de pista 
        				//texto -> Nombre de la pista
				      	
        				mensaje = NOM_PISTA;		
        				i++;
        				for ( j=i+1; j<=i + midi->pistas[npista].cabecera.data[i]; j++ )
        				{
        					tmp[0] = midi->pistas[npista].cabecera.data[j];
        					tmp[1] = '\0';
        					texto = concat(texto,tmp,cEOA);
        				}	
        				i=j-1;
        				break;
        			case 0x04 : //* Nombre de instrumento 
        				//texto -> Nombre del instrumento
				      
        				mensaje = NOM_INST;
        				i++;
        				for ( j=i+1; j<=i + midi->pistas[npista].cabecera.data[i]; j++ )
        				{
        					tmp[0] = midi->pistas[npista].cabecera.data[j];
        					tmp[1] = '\0';
        					texto = concat(texto,tmp,cEOA);
        				}	
        				i=j-1;
	 			      
        				//printf("Nombre instrumento: %s\n", texto);
	 			      
        				break;
        			case 0x05 : // Letras
        				//texto -> Letras
				      	
        				mensaje = LETRA;
        				i++;
        				for ( j=i+1; j<=i + midi->pistas[npista].cabecera.data[i]; j++ )
        				{
        					tmp[0] = midi->pistas[npista].cabecera.data[j];
        					tmp[1] = '\0';
        					texto = concat(texto,tmp,cEOA);
        					
        				}	

    					//printf("Letras %d\n", npista);


        				i=j-1;
        				break;
        			case 0x06 : // Marcador de posicion
        				//texto -> Posicion
				      	
        				mensaje = POSICION;
        				i++;
        				for ( j=i+1; j<=i + midi->pistas[npista].cabecera.data[i]; j++ )
        				{
        					tmp[0] = midi->pistas[npista].cabecera.data[j];
        					tmp[1] = '\0';
        					texto = concat(texto,tmp,cEOA);
        				}	
        				i=j-1;
        				break;
        			case 0x07 : // Marcador de referencia
        				//texto -> Punto de cola
				      	
        				mensaje = REFERENCIA;
        				i++;
        				for ( j=i+1; j<=i + midi->pistas[npista].cabecera.data[i]; j++ )
        				{
        					tmp[0] = midi->pistas[npista].cabecera.data[j];
        					tmp[1] = '\0';
        					texto = concat(texto,tmp,cEOA);
        				}	
        				i=j-1;
        				break;
        			case 0x2F : // Marcador de fin de pista
				      	
        				mensaje = FIN_PISTA;
        				i++;
        				for ( j=i+1; j<=i + midi->pistas[npista].cabecera.data[i]; j++ )
        				{
        					tmp[0] = midi->pistas[npista].cabecera.data[j];
        					tmp[1] = '\0';
        					texto = concat(texto,tmp,cEOA);
        				}	
        				i=j-1;
        				break;
        			case 0x51 : // tempo
        				//dato3 -> tempo
			  	      	
			  	      	mensaje = AJUS_TEMPO;
			  	      	tempo = (midi->pistas[npista].cabecera.data[i+2]*0x100 + midi->pistas[npista].cabecera.data[i+3])*0x100 + midi->pistas[npista].cabecera.data[i+4];
			  	      	tempo = 60000000.0 / tempo;
			  	      	dato3 = tempo;
			  	      	i=i+4; break;
        			case 0x58 : // compas
        				//dato1 -> numerados
        				//dato2 -> denominador
			  	      
        				mensaje = COMPAS;
			  	      	dato1 = midi->pistas[npista].cabecera.data[i+2];
			  	      	
			  	      	switch ( midi->pistas[npista].cabecera.data[i+3] ) 
			  	      	{
			  	      		case 1 : 
			  	      			dato2 = 2; 
			  	      			break;
			  	      		case 2 : 
			  	      			dato2 = 4; 
			  	      			break;
			  	      		case 3 : 
			  	      			dato2 = 8;
			  	      			break;
			  	      		case 4 : 
			  	      			dato2 = 16;
			  	      			break;
			  	      		
			  	      	}
			  	      	i=i+5; 
			  	      	break;
			  	    case 0x59 : // tonalidad
			  	    	//dato1 -> tono
			  	    	//dato2 -> modo (0 menor 1 mayor)
			              
				  
			  	    	mensaje = TONALIDAD;
/*			  	    	
			  	    	if ( midi->pistas[npista].cabecera.data[i+2]>127 )
			  	    	{
			  	    		//printf("data[i+2]: %d\n", midi->pistas[npista].cabecera.data[i+2]);
			  	    		dato1 = midi->pistas[npista].cabecera.data[i+2]-256;
			  	    		//aux = aux-256;
			  	    		//printf("if aux: %d\n", aux);
			  	    	}
			  	    	else
			  	    	{
			  	    		dato1 = midi->pistas[npista].cabecera.data[i+2];
			  	    		//printf("else: %d", aux);
			  	    	}
			  	    	// printf("Tonalidad: %s",tono[aux+7]);
			  	    	dato1 = dato1+7;
			  	    	if ( midi->pistas[npista].cabecera.data[i+3] )
			  	    		dato2 = 1;
			  	    	else 
			  	    		dato2 = 0;
*/
			  	    	dato1 = midi->pistas[npista].cabecera.data[i+2];
			  	    	dato2 =  midi->pistas[npista].cabecera.data[i+3];
				  
			  	    	i=i+3; 
			  	    	break;
			  	    case 0x7F : // Especifico
			  	      
			  	    	//printf("(especifico, %d bytes)\n",midi.pistas[npista].cabecera.data[i+1]);
			  	    	mensaje = INFO_ESPEC;	
			  	    	i=i + midi->pistas[npista].cabecera.data[i+1]+1; 
			  	    	break;
			  	    default   : // Desconocido 
			              
			  	    	mensaje = DESCONOCIDO;
			  	    	//printf("(metaevento ?, %d bytes)\n",midi.pistas[npista].cabecera.data[i+1]);
			  	    	i=i + midi->pistas[npista].cabecera.data[i+1]+1; break;
        		}
        	}
	    
        	else if ( midi->pistas[npista].cabecera.data[i] > 0x7F )  // APARECE UN BYTE DE ESTADO 
        	{
        		tipo = CANAL;
        		status = midi->pistas[npista].cabecera.data[i]/0x10;
        		switch ( status ) 
        		{
        			case 0x8 : // Nota_off 
			               //canal -> canal
			               //dato1 -> nota
			               //dato2 -> vel
		             
			             mensaje = NOTA_OFF;
			             canal = midi->pistas[npista].cabecera.data[i] % 0x10 + 1;
			             dato1 = midi->pistas[npista].cabecera.data[i+1];
			             dato2 = midi->pistas[npista].cabecera.data[i+2];
			             i+=2;
			             break;
        			case 0x9 : // Nota_on 
        				//canal -> canal
        				//dato1 -> nota
        				//dato2 -> vel
		             
        				mensaje = NOTA_ON;
        				canal = midi->pistas[npista].cabecera.data[i] % 0x10 + 1;
        				dato1 = midi->pistas[npista].cabecera.data[i+1];
        				dato2 = midi->pistas[npista].cabecera.data[i+2];
        				i+=2;
        				//truco de las 6 notas
        				//if(dato2>0)
        					//nTruco++;
        				break;
        			case 0xA : // Postpulsacion Polifonica 
        				//canal -> canal
        				//dato1 -> nota
        				//dato2 -> vel
		             
        				mensaje = POST_POLIF;
        				canal = midi->pistas[npista].cabecera.data[i] % 0x10 + 1;
        				dato1 = midi->pistas[npista].cabecera.data[i+1];
        				dato2 = midi->pistas[npista].cabecera.data[i+2];
        				i+=2;
        				break;
        			case 0xB : // Control
        				//canal -> canal
        				//dato1 -> c
        				//dato2 -> v
		            
        				mensaje = CONTROL;
        				canal = midi->pistas[npista].cabecera.data[i] % 0x10 + 1;
        				dato1 = midi->pistas[npista].cabecera.data[i+1];
        				dato2 = midi->pistas[npista].cabecera.data[i+2];
        				i+=2;
        				break;
        			case 0xC :  //C_PROGRAMA
        				//canal -> canal
        				//dato1 -> patch
		            
        				//truco de las 6 notas
        				//if(nTruco>6)
        				//{
	        				mensaje = C_PROGRAMA;
	        				canal = midi->pistas[npista].cabecera.data[i] % 0x10 + 1;
	        				dato1 = midi->pistas[npista].cabecera.data[i+1];
        				//}
        				i++;
		            
        				//printf("Cambio programa: %d %d\n", canal, dato1);
       					break;
       				case 0xD : // Postpulsaci�n de canal
       					//canal -> canal
       					//dato1 -> v
		             
       					mensaje = POST_CANAL;
       					canal = midi->pistas[npista].cabecera.data[i] % 0x10 + 1;
       					dato1 = midi->pistas[npista].cabecera.data[i+1];
       					i++;
       					break;
       				case 0xE : // Cambio altura
       					//canal -> canal
       					//dato1 -> valor 
	             
       					mensaje = ALTURA;
       					canal = midi->pistas[npista].cabecera.data[i] % 0x10 + 1;
       					dato1 = midi->pistas[npista].cabecera.data[i+1] + 0x80*midi->pistas[npista].cabecera.data[i+2]-0x2000;
       					i+=2;
       					break;
       				case 0xF : // sysex 
       					//?????
       					//lo guardo en texto
	             
       					if ( midi->pistas[npista].cabecera.data[i] % 0x10 == 0 ) // sysex 
       					{
       						mensaje = SISEX;
       						texto = strdup("");
       						do 
       						{
				        
       							tmp[0] = midi->pistas[npista].cabecera.data[i]; 
        						tmp[1] = '\0';
        						texto = concat(texto,tmp,cEOA);
        						i++;
        					} while ( midi->pistas[npista].cabecera.data[i] != 0xF7 );
        					tmp[0] = midi->pistas[npista].cabecera.data[i]; 
        					tmp[1] = '\0';
        					texto = concat(texto,tmp,cEOA);
        				}
        				else
        					i++; // LOS MENSAJES DE SISTEMA NO ESTAN IMPLEMENTADOS TODAVIA 
        				break;
        		}
        	}
	    
        	else  // no hay byte de estado: hay running status 
        	{
        		switch ( status ) 
        		{
        			case 0x8 : // Nota_off 
        				//dato1 -> nota
        				//dato2 -> vel
		             
        				dato1 = midi->pistas[npista].cabecera.data[i];
        				dato2 = midi->pistas[npista].cabecera.data[i+1];
        				i++;
        				break;
        			case 0x9 : // Nota_on 
        				//dato1 -> nota
        				//dato2 -> vel
		            
        				dato1 = midi->pistas[npista].cabecera.data[i];
        				dato2 = midi->pistas[npista].cabecera.data[i+1];
        				i++;
        				break;
        			case 0xA : // Postpulsacion Polifonica 
        				//dato1 -> nota
        				//dato2 -> vel
		            
        				dato1 = midi->pistas[npista].cabecera.data[i];
        				dato2 = midi->pistas[npista].cabecera.data[i+1];
        				i++;
        				
        				//if(dato2>0)
        				//	nTruco++;
        				
        				break;
        			case 0xB : // Control
        				//dato1 -> c
        				//dato2 -> v
		            
        				dato1 = midi->pistas[npista].cabecera.data[i];
        				dato2 = midi->pistas[npista].cabecera.data[i+1];
        				i++;
        				break;
        			case 0xC : // C_PROGRAMA
        				//dato1 -> patch, programa
		            
        				//truco de las 6 notas
        				//if(nTruco>6)
        					dato1 = midi->pistas[npista].cabecera.data[i];
        				break;
        			case 0xD : // Postpulsaci�n de canal
        				//dato1 -> v
		            
        				dato1 = midi->pistas[npista].cabecera.data[i];
        				break;
        			case 0xE : // Cambio altura
        				//dato1 -> valor 
		             
        				dato1 = midi->pistas[npista].cabecera.data[i+1] + 0x80*midi->pistas[npista].cabecera.data[i+2]-0x2000;
        				i++;
        				break;
        			case 0xF : // sysex 
        				// ?????
        				//lo guardo en texto
		             
        				//if ( midi.pistas[npista].cabecera.data[i] % 0x10 == 0 ) 
        				//{
        				//mensaje = SISEX;
        				//texto = strdup("");
        				//     do {
        				//       tmp[0] = midi.pistas[npista].cabecera.data[i]; 
        				//       tmp[1] = '\0';
        				//       texto = concat(texto,tmp,cEOA);
        				//       i++;
        				//     } while ( midi.pistas[npista].cabecera.data[i] != 0xF7 );
        				//       tmp[0] = midi.pistas[npista].cabecera.data[i]; 
        				//       tmp[1] = '\0';
        				//       texto = concat(texto,tmp,cEOA);
        				//   }
        				i++;
        				break;
        		} 
        	}  // del else 
	    
        	int k, guardar;
        	//comprobar que no se inserte un evento NOTE-ON de una nota que ya está sonando
        	guardar = 1;
        	if(mensaje == NOTA_ON && dato2 > 0) //NOTA-ON velocidad > 0
        	{
	        	for(k=n-1;k>=0;k--)
	        	{
	        		if(midi->pistas[npista].evento[k].mensaje == NOTA_ON 	
	        				&& midi->pistas[npista].evento[k].dato2 > 0		//velocidad
	        				&& midi->pistas[npista].evento[k].dato1 == dato1)//altura
	        					
	        		{
	        			guardar = 0;
	        			k=0;
	        		}

	        		if(midi->pistas[npista].evento[k].mensaje == NOTA_ON 	 
	        				&& midi->pistas[npista].evento[k].dato2 == 0	//velocidad
	        				&& midi->pistas[npista].evento[k].dato1 == dato1)//altura
	        		{
	        			k=0;
	        		}
	        		
	        		if(midi->pistas[npista].evento[k].mensaje == NOTA_OFF 	 
	        				&& midi->pistas[npista].evento[k].dato1 == dato1)//altura
	        		{
	        			k=0;
	        		}
	        		
	        		
	        	}
        	}
        	
        	//comprobar que los NOTE-ON VEL=0 sean sobre note-on que todavia estan activos
        	if(mensaje == NOTA_ON && dato2 == 0)	//NOTA-ON velocidad = 0
        	{
        		for(k=n-1;k>=0;k--)
        		{
        			//que sea NOTA_OFF de que no se corresponde con ningun NOTA_ON 
        			if(k == 0) 
        			{
        				if(midi->pistas[npista].evento[0].mensaje != NOTA_ON
        						|| midi->pistas[npista].evento[k].dato1 == dato1
        						|| midi->pistas[npista].evento[k].dato2 == 0)
        				{
        					guardar = 0;
        				}
        			}

	        		if(midi->pistas[npista].evento[k].mensaje == NOTA_ON 	
	        				&& midi->pistas[npista].evento[k].dato1 == dato1//altura
	        				&& midi->pistas[npista].evento[k].dato2 == 0)	//velocidad
	        		{
	        			guardar = 0;
	        			k=0;
	        		}

	        		if(midi->pistas[npista].evento[k].mensaje == NOTA_OFF	
	        				&& midi->pistas[npista].evento[k].dato1 == dato1)//altura
	        		{
	        			guardar = 0;
	        			k=0;
	        		}
	        		
	        		if(midi->pistas[npista].evento[k].mensaje == NOTA_ON 	
	        				&& midi->pistas[npista].evento[k].dato1 == dato1//altura
	        				&& midi->pistas[npista].evento[k].dato2 > 0)	//velocidad
	        		{
	        			k=0;
	        		}
        		}
        	}
        	
        	//comprobar que los NOTE-OFF sean sobre note-on que todavia estan activos
        	if(mensaje == NOTA_OFF )	//NOTA-ON velocidad = 0
        	{
        		for(k=n-1;k>=0;k--)
        		{
        			//que sea NOTA_OFF de que no se corresponde con ningun NOTA_ON 
        			if(k == 0) 
        			{
        				if(midi->pistas[npista].evento[0].mensaje != NOTA_ON
        						|| midi->pistas[npista].evento[k].dato1 == dato1
        						|| midi->pistas[npista].evento[k].dato2 == 0)
        				{
        					guardar = 0;
        				}
        			}
        			
	        		if(midi->pistas[npista].evento[k].mensaje == NOTA_ON 	
	        				&& midi->pistas[npista].evento[k].dato1 == dato1//altura
	        				&& midi->pistas[npista].evento[k].dato2 == 0)	//velocidad
	        		{
	        			guardar = 0;
	        			k=0;
	        		}

	        		if(midi->pistas[npista].evento[k].mensaje == NOTA_OFF	
	        				&& midi->pistas[npista].evento[k].dato1 == dato1)//altura
	        		{
	        			guardar = 0;
	        			k=0;
	        		}
	        		
	        		if(midi->pistas[npista].evento[k].mensaje == NOTA_ON 	
	        				&& midi->pistas[npista].evento[k].dato1 == dato1//altura
	        				&& midi->pistas[npista].evento[k].dato2 > 0)	//velocidad
	        		{
	        			k=0;
	        		}
        		}
        	}
        	
        	//	guardamos el evento
        	if(guardar == 1)
        	{
	 			midi->pistas[npista].evento = (TEvento*)realloc(midi->pistas[npista].evento,(n+1)*sizeof(TEvento));
	 			midi->pistas[npista].evento[n].tipo    = tipo;
	 			midi->pistas[npista].evento[n].mensaje = mensaje;
	 			midi->pistas[npista].evento[n].dato1   = dato1;
	 			midi->pistas[npista].evento[n].dato2   = dato2;
	 			midi->pistas[npista].evento[n].dato3   = dato3;
	 			midi->pistas[npista].evento[n].canal   = canal;
	 			midi->pistas[npista].evento[n].texto   = strdup(texto);
//	 			printf("pista %d | Evento %d |%s\n", npista, n, texto);
	 			midi->pistas[npista].evento[n].tini    = tini;
	 			midi->pistas[npista].evento[n].t_delta = t_delta;				
	
	 			n++;
        	}
        } while ( i<midi->pistas[npista].cabecera.size-1 ); //fin de los datos de la pista
        
        midi->pistas[npista].cabecera.numeventos = n;
	  
	}// lectura de pistas
   
	for (i=0;i<midi->cabecera.numpistas;i++)
	{
		midi->pistas[i].nota = AnalizaNotas(midi->pistas[i].evento, midi->pistas[i].cabecera.numeventos, &(midi->pistas[i].cabecera.numnotas));
	}
	for (i=0;i<midi->cabecera.numpistas;i++)
	{
		CargaDescriptoresPista(*midi, i, &(midi->pistas[i].descriptores), DuracionPistaMasLarga(*midi), DuracionCancion(*midi));
	}
	CargaDescriptoresMidi(*midi, &(midi->descriptores));
	fclose(fin);
	//return midi;

}// fin funcion  

/**********************************************************************
Funcion: EscribeLin(TMidi midi,char *nombre,FILE *fich)
Argumentos: El Midi a imrpimir
Accion: Escribe en fich los descriptores de midi (en una linea) 
	el fichero debe estar abierto
**********************************************************************/

int
maxPolyphony(TMidi midi, int nPista)
{
	int i;
	int max, actual;
	
	max=0;
	actual=0;
	
	for(i=0; i<midi.pistas[nPista].cabecera.numeventos; i++)
	{
		if(midi.pistas[nPista].evento[i].mensaje == NOTA_ON)
		{
			if(midi.pistas[nPista].evento[i].dato2 > 0)
			{	
				actual++;
			}
			else
			{
				actual--;
			}
		}
		else
		{
			if(midi.pistas[nPista].evento[i].mensaje == NOTA_OFF)
			{
				actual--;
			}
		}
		
		if(actual > max)
		{
			max = actual;
		}
	}
	
	return max;
}

/*
float
Polyphony(TMidi midi, int nPista)
{
	int i;
	int , actual, hayPolifonia;
	
	actual=0;
	 = 0;
	hayPolifonia = 0;
	
	for(i=0; i<midi.pistas[nPista].cabecera.numeventos; i++)
	{
		if(midi.pistas[nPista].evento[i].mensaje == NOTA_ON)
		{
			if(midi.pistas[nPista].evento[i].dato2 > 0)
			{	
				actual++;
			}
			else
			{
				actual--;
			}
		}
		else
		{
			if(midi.pistas[nPista].evento[i].mensaje == NOTA_OFF)
			{
				actual--;
			}
		}
		
		if(actual > 1)
		{
			hayPolifonia++;
		}
	}
	//printf("Pista %d, Numero notas: %d\n", nPista, midi.pistas[nPista].cabecera.numnotas);
	
	if(midi.pistas[nPista].cabecera.numnotas > 0)
	{
		 = hayPolifonia / midi.pistas[nPista].cabecera.numnotas;
	}
	else
	{
		 = -1;
	}

	
	return ;
}
*/

double
avgPolyphony(TMidi midi, int nPista, int ocupacion)
{
	int i;
	double avg;
	int actual, hayPolifonia;
	int tInicio, tFin;
	
	actual=0;
	avg = 0;
	hayPolifonia = 0;
	tInicio = 0;
	tFin = 0;

/*	
	if(nPista == 9)
		printf("----------Empiezo");
*/
	
	for(i=0; i<midi.pistas[nPista].cabecera.numeventos; i++)
	{
		if(midi.pistas[nPista].evento[i].mensaje == NOTA_ON || midi.pistas[nPista].evento[i].mensaje == NOTA_OFF)
		{
			
			tInicio = tFin;
			tFin = midi.pistas[nPista].evento[i].tini;

			avg = avg + actual*(tFin - tInicio);
/*			
			if (actual<0)
				printf("---------------------actual: %d fin: %d inicio: %d\n", actual, tFin, tInicio);
			
			if((tFin - tInicio) < 0)
				printf("---------------------fin: %d inicio: %d\n", tFin, tInicio);
*/			
			
			if(midi.pistas[nPista].evento[i].mensaje == NOTA_ON)
			{
				if(midi.pistas[nPista].evento[i].dato2 > 0)
				{	
					actual++;
/*
					if(nPista == 9)
						printf("-------------------------------- NOTA_ON   %d\n", actual);
*/
				}
				else
				{
					actual--;
/*
					if(nPista == 9)
						printf("-------------------------------- NOTA_OFF1 %d\n", actual);
*/
				}
			}
			else
			{
				if(midi.pistas[nPista].evento[i].mensaje == NOTA_OFF)
				{
					actual--;
/*					
					if(nPista == 9)
						printf("-------------------------------- NOTA_OFF2 %d\n", actual);
*/						
				}
			}
		}
	}

	if (ocupacion > 0)
	{
		//printf("---------------------avg: %.2f\n", avg);

		avg = avg / ocupacion;
	}

	return avg;
}

double
polyphonyRate(TMidi midi, int nPista, int ocupacion)
{
	int i;
	double avg;
	int actual, hayPolifonia;
	int tInicio, tFin;
	
	actual=0;
	avg = 0;
	hayPolifonia = 0;
	tInicio = 0;
	tFin = 0;
	
	
	for(i=0; i<midi.pistas[nPista].cabecera.numeventos; i++)
	{
		if(midi.pistas[nPista].evento[i].mensaje == NOTA_ON || midi.pistas[nPista].evento[i].mensaje == NOTA_OFF)
		{
			tInicio = tFin;
			tFin = midi.pistas[nPista].evento[i].tini;

/*			
			if (actual<0)
				printf("---------------------actual: %d fin: %d inicio: %d\n", actual, tFin, tInicio);
			
			if((tFin - tInicio) < 0)
				printf("---------------------fin: %d inicio: %d\n", tFin, tInicio);
*/
			
			if(actual > 1)
			{
				avg = avg + (tFin - tInicio);
			}

			if(midi.pistas[nPista].evento[i].mensaje == NOTA_ON)
			{
				if(midi.pistas[nPista].evento[i].dato2 > 0)
				{	
					actual++;
				}
				else
				{
					actual--;
				}
			}
			else
			{
				if(midi.pistas[nPista].evento[i].mensaje == NOTA_OFF)
				{
					actual--;
				}
			}
		}
	}

	if (ocupacion > 0)
	{
		//printf("---------------------avg: %.2f\n", avg);

		avg = avg / (double)ocupacion;
	}
	
	return avg;
}
