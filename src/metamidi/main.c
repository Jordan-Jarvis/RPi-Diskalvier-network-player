/*
Copyright (c) 2009 Jose M. Inesta <inesta@dlsi.ua.es>
Copyright (c) 2009 Pedro J. Ponce de Leon <pierre@dlsi.ua.es>
Copyright (c) 2009 Carlos Perez Sancho <cperez@dlsi.ua.es>
Copyright (c) 2009 Antonio Pertusa Ibanez <pertusa@dlsi.ua.es>
Copyright (c) 2009 David Rizo Valero <drizo@dlsi.ua.es>
Copyright (c) 2009 Tomas Perez Garcia <tperez@dlsi.ua.es>
Copyright (c) 2009 Universitat d'Alacant
*/
#include <stdio.h>
#include "extractorXML.h"
#include "tmidi.h"
#include "define.h"


char*
extraerMetadatos(TMidi m)
{
	char *aux; 
	
	aux = getMidiFile(m);

	return aux;
}

char*
formatearSalida(char *texto, char *variable)
{
	char *aux;
	char *salida;

	/*
	printf("********************* %s\n", texto);
	printf("********************* %s\n", variable);
	*/
	salida = strdup("");
	aux = (char*)malloc(sizeof(char)*(NBLANKS+10));
	
	salida = concat(salida, texto, cEOA);
	sprintf(aux, "%*s", (int)(NBLANKS-strlen(texto)), "");
	salida = concat(salida, aux, cEOA);
	salida = concat(salida, variable, "\n", cEOA);
		
	free(aux);

	return salida;
}


char*
extraerDescriptores(TMidi m)
{
	int i;
	char *salida, *aux;

  	
  	salida = strdup("");
  	aux = (char*)malloc(sizeof(char)*100);
  	
  	sprintf(aux, "------- Midi features --------");
  	salida = concat(salida, aux, "\n", cEOA);
  	

  	//name
  	salida = concat(salida, formatearSalida("name:", m.descriptores.path), cEOA);
  	
   	//metaeventtext
  	salida = concat(salida, formatearSalida("text metaevent:", m.descriptores.texto), cEOA);
  	
  	//size
	sprintf(aux, "%ld", m.descriptores.bytes);
	salida = concat(salida, formatearSalida("size:", aux), cEOA);

  	//format
	sprintf(aux, "%d", m.descriptores.formato);
	salida = concat(salida, formatearSalida("format:", aux), cEOA);
  	
  	//num traks
  	sprintf(aux, "%d", m.descriptores.numpistas);
  	salida = concat(salida, formatearSalida("num tracks:", aux), cEOA);
  	
  	//resolution
  	sprintf(aux, "%d", m.descriptores.division);
  	salida = concat(salida, formatearSalida("resolution:", aux), cEOA);
  	
  	//tempo
  	if(m.descriptores.tempo == -1)
  		sprintf(aux,"none");
  	else
  		sprintf(aux,"%.*f", NDEC, m.descriptores.tempo);
  	salida = concat(salida, formatearSalida("tempo:", aux), cEOA);
  	
  	//tempo changes
  	sprintf(aux,"%d", m.descriptores.c_tempo);
  	salida = concat(salida, formatearSalida("tempo changes:", aux), cEOA);
  
  	//meter
  	/*
  	if(m.descriptores.num_compas == -1 || m.descriptores.den_compas == -1)
  		sprintf(aux, "none");
  	else
  		sprintf(aux, "%d/%d",m.descriptores.num_compas,m.descriptores.den_compas);
  	salida = concat(salida, formatearSalida("meter:", aux), cEOA);
  	 */
  	salida = concat(salida, formatearSalida("meter:", m.descriptores.compases), cEOA);

  	//meter changes
  	sprintf(aux, "%d",m.descriptores.c_metrica);
  	salida = concat(salida, formatearSalida("meter changes:", aux), cEOA);
  	
  	//key
  	salida = concat(salida, formatearSalida("key:", m.descriptores.key), cEOA);
  	
  	//key changes
  	sprintf(aux, "%d",m.descriptores.c_tono);
  	salida = concat(salida, formatearSalida("key changes:", aux), cEOA);
  	
  	//instruments
  	salida = concat(salida, formatearSalida("instruments: ",m.descriptores.instrumentos), cEOA );

  	//percussion
  	salida = concat(salida, formatearSalida("percussion: ",m.descriptores.percusion), cEOA );

  	//duration
  	sprintf(aux, "%d",m.descriptores.duracion);
  	salida = concat(salida, formatearSalida("duration:", aux), cEOA);
  	
  	//has sysex
  	sprintf(aux, "%d",m.descriptores.hasSysEx);
	salida = concat(salida, formatearSalida("has sysex:", aux), cEOA);

  	for(i=0;i<m.cabecera.numpistas;i++)
  	{
    	sprintf(aux, "------ Features of track %d ----", i);
    	salida = concat(salida, aux, "\n", cEOA);
    	
   		//metaeventtext
    	sprintf(aux, "%d", m.pistas[i].descriptores.maxPolyphony);
    	salida = concat(salida, formatearSalida("text metaevent:", m.pistas[i].descriptores.texto), cEOA);

    	//channel
    	sprintf(aux, "%d",m.pistas[i].descriptores.canal);
    	salida = concat(salida, formatearSalida("channel:", aux), cEOA);

    	//duration
    	sprintf(aux, "%d",m.pistas[i].descriptores.duracion);
    	salida = concat(salida, formatearSalida("duration:", aux), cEOA);
    	
    	//duration rate
    	sprintf(aux, "%.*f", NDEC, m.pistas[i].descriptores.d_absoluta);
    	salida = concat(salida, formatearSalida("duration rate:", aux), cEOA);
    	
    	//sounding
    	sprintf(aux, "%d",m.pistas[i].descriptores.d_sonido);
    	salida = concat(salida, formatearSalida("occupation:", aux), cEOA);

    	//sounding rate
    	sprintf(aux, "%.*f", NDEC, m.pistas[i].descriptores.sonido);
    	salida = concat(salida, formatearSalida("occupation rate:", aux), cEOA);

    	//polyphony duration rate
    	sprintf(aux, "%.*f", NDEC, m.pistas[i].descriptores.polifonica);
    	salida = concat(salida, formatearSalida("polyphony duration rate:", aux), cEOA);
    	
    	//max simultaneous notes
    	sprintf(aux, "%d", m.pistas[i].descriptores.maxPolyphony);
    	salida = concat(salida, formatearSalida("max polyphony:", aux), cEOA);
    	
    	//avg simultaneous notes
    	sprintf(aux, "%.*f", NDEC, m.pistas[i].descriptores.avgPolyphony);
    	salida = concat(salida, formatearSalida("avg polyphony:", aux), cEOA);
    	
    	//low pitch
    	sprintf(aux, "%d",m.pistas[i].descriptores.nota_baja);
    	salida = concat(salida, formatearSalida("low pitch:", aux), cEOA);

    	//high pitch
    	sprintf(aux, "%d",m.pistas[i].descriptores.nota_alta);
    	salida = concat(salida, formatearSalida("high pitch:", aux), cEOA);

    	//modulations
    	sprintf(aux, "%d",m.pistas[i].descriptores.n_msgModulacion);
    	salida = concat(salida, formatearSalida("modulations:", aux), cEOA);
    	
    	//aftertouches
    	sprintf(aux, "%d",m.pistas[i].descriptores.n_msgPostPul);
    	salida = concat(salida, formatearSalida("aftertouches:", aux), cEOA);
    	
    	//pitch bends
    	sprintf(aux, "%d",m.pistas[i].descriptores.n_msgAltura);
    	salida = concat(salida, formatearSalida("pitch bends:", aux), cEOA);

    	//program changes
    	//sprintf(aux, "%d",m.pistas[i].descriptores.n_cambiosPrograma);
    	salida = concat(salida, formatearSalida("program changes:", m.pistas[i].descriptores.cambiosPrograma), cEOA);
  	}
	salida = concat(salida, "******************************************************************", "\n", cEOA);

  	return salida;
	//return "";
}


char*
EscribeLin(TMidi midi)
{
	int n;
	char *salida, *aux;
	
	salida=strdup("");
	
	aux=(char*)malloc(sizeof(char)*50);

	//name
	salida = concat(salida, "'", midi.descriptores.path, "';", cEOA);
	
   	//metaeventtext
  	salida = concat(salida, "'", midi.descriptores.texto, "';", cEOA);
  	
  	//size
	sprintf(aux, "%ld", midi.descriptores.bytes);
	salida = concat(salida, aux, ";", cEOA);

	//escribimos el formato del midi 
	sprintf(aux, "%d", midi.descriptores.formato);
	salida = concat(salida, aux, ";", cEOA);
	
  	//num traks
  	sprintf(aux, "%d", midi.descriptores.numpistas);
  	salida = concat(salida, aux, ";", cEOA);

	// division 
	sprintf(aux, "%d", midi.descriptores.division);
  	salida = concat(salida, aux, ";", cEOA);

	// tempo inicial 
	sprintf(aux, "%.*f", NDEC, midi.descriptores.tempo);
  	salida = concat(salida, aux, ";", cEOA);
  	
  	//tempo changes
  	sprintf(aux,"%d", midi.descriptores.c_tempo);
  	salida = concat(salida, aux, ";", cEOA);

  	//meter
//  	sprintf(aux, "%d/%d",midi.descriptores.num_compas, midi.descriptores.den_compas);
 // 	salida = concat(salida, aux, ";", cEOA);
  	salida = concat(salida, midi.descriptores.compases, ";", cEOA);
  	//meter changes
  	sprintf(aux, "%d",midi.descriptores.c_metrica);
  	salida = concat(salida, aux, ";", cEOA);

  	//key
  	salida = concat(salida, midi.descriptores.key, ";", cEOA);
  	
  	//key changes
  	sprintf(aux, "%d",midi.descriptores.c_tono);
  	salida = concat(salida, aux, ";", cEOA);

  	//instruments
  	salida = concat(salida, midi.descriptores.instrumentos, ";", cEOA );

  	//percussion
  	salida = concat(salida, midi.descriptores.percusion, ";", cEOA );

  	//duration
  	sprintf(aux, "%d",midi.descriptores.duracion);
  	salida = concat(salida, aux, ";", cEOA);
  	
  	//has sysex
  	sprintf(aux, "%d",midi.descriptores.hasSysEx);
	salida = concat(salida, aux, ";", cEOA);

  	

/***********************************************************
	FIN DE LA INFORMACION DEL MIDI 
	INFORMACION DE CADA PISTA
************************************************************/ 
	
	for(n=0;n<midi.descriptores.numpistas;n++){

		// numero de pista 
		sprintf(aux, "%d",n);
		salida = concat(salida, "|", aux, ";", cEOA);
		
		// texto 
		salida = concat(salida, "'", midi.pistas[n].descriptores.texto, "';", cEOA);

		// canal inicial 
		sprintf(aux,"%d",midi.pistas[n].descriptores.canal);
		salida = concat(salida, aux, ";", cEOA);
		
    	//duration
    	sprintf(aux, "%d",midi.pistas[n].descriptores.duracion);
    	salida = concat(salida, aux, ";", cEOA);
    	
    	//duration rate
    	sprintf(aux, "%.*f", NDEC, midi.pistas[n].descriptores.d_absoluta);
    	salida = concat(salida, aux, ";", cEOA);

    	//sounding
    	sprintf(aux, "%d",midi.pistas[n].descriptores.d_sonido);
    	salida = concat(salida, aux, ";", cEOA);

    	//sounding rate
    	sprintf(aux, "%.*f", NDEC, midi.pistas[n].descriptores.sonido);
    	salida = concat(salida, aux, ";", cEOA);

    	//polyphony rate
    	sprintf(aux, "%.*f", NDEC, midi.pistas[n].descriptores.polifonica);
    	salida = concat(salida, aux, ";", cEOA);
    	
    	//max simultaneous notes
    	sprintf(aux, "%d", midi.pistas[n].descriptores.maxPolyphony);
    	salida = concat(salida, aux, ";", cEOA);
    	
    	//avg simultaneous notes
    	sprintf(aux, "%.*f", NDEC, midi.pistas[n].descriptores.avgPolyphony);
    	salida = concat(salida, aux, ";", cEOA);
    	
    	//low pitch
    	sprintf(aux, "%d",midi.pistas[n].descriptores.nota_baja);
    	salida = concat(salida, aux, ";", cEOA);

    	//high pitch
    	sprintf(aux, "%d",midi.pistas[n].descriptores.nota_alta);
    	salida = concat(salida, aux, ";", cEOA);

    	//modulations
    	sprintf(aux, "%d",midi.pistas[n].descriptores.n_msgModulacion);
    	salida = concat(salida, aux, ";", cEOA);
    	
    	//aftertouches
    	sprintf(aux, "%d", midi.pistas[n].descriptores.n_msgPostPul);
    	salida = concat(salida, aux, ";", cEOA);
    	
    	//pitch bends
    	sprintf(aux, "%d",midi.pistas[n].descriptores.n_msgAltura);
    	salida = concat(salida, aux, ";", cEOA);

    	//program changes
    	//sprintf(aux, "%d",midi.pistas[n].descriptores.n_cambiosPrograma);
    	salida = concat(salida, midi.pistas[n].descriptores.cambiosPrograma, ";", cEOA);
    	
/*
		// long en bytes 
		printf("%d;",midi.pistas[n].descriptores.longbytes);
	// programa inicial 
		printf("%d;",midi.pistas[n].descriptores.programa);
	// mono o poly (tasa ahora luego cambio) 
		printf("%f;",midi.pistas[n].descriptores.polifonica);
	// uso de la pista 
		printf("%f;",midi.pistas[n].descriptores.d_absoluta);
	// cambios programa 
		printf("%d;",midi.pistas[n].descriptores.n_cambiosPrograma);
	// cambios control 
		printf("%d;",midi.pistas[n].descriptores.n_msgModulacion);
	// cambios altura 
		printf("%d;",midi.pistas[n].descriptores.n_msgAltura);
	// cambios postpul 
		printf("%d;",midi.pistas[n].descriptores.n_msgPostPul);
*/		
	}
	// fin del fichero... saltamos de linea
	printf("\n");
	
	
	free(aux);
	
	return salida;
}




int
main(int argc, char **argv)
{
	int error, ok;
	char* salida;
	FILE *fout;
	TMidi midi;

	
	error = 0;
	salida = NULL;

	if(argc == 2)
	{
		if(strcmp(argv[1], "--help") == 0)
		{
			salida=strdup("METAMIDI: Standard MIDI File Metadata Extractor\n\
Developed by:\n\
Pattern Recognition and Artificial Intelligence Group\n\
http://grfia.dlsi.ua.es\n\
Departamento de lenguajes y sistemas informaticos,\n\
http://www.dlsi.ua.es\n\
University of Alicante.\n\
http://www.ua.es\n\
Usage: metamidi -{r|x|l} file [-o fileoutput]\n\
-r file			: show metadata in register format\n\
-l file			: show metadata in line format\n\
-x file			: show metadata in xml format\n\
Option: \n\
-o fileoutput	: optional fileoutput");
		}
		else
		{
			error = 1;
		}
	}
	else
	{
		if (argc > 2)
		{
			//printf("ficheros: %s\n" , argv[2]);
			CargaMidi(&midi, argv[2], &ok);
			//printf("Ok: %d\n", ok);
			if(ok)
			{
				if(strcmp(argv[1], "-r") == 0)
				{
					salida = extraerDescriptores(midi);
				}
				else
				{
					if(strcmp(argv[1], "-x") == 0)
					{
						salida = extraerMetadatos(midi);
					}
					else
					{
						if(strcmp(argv[1], "-l") == 0)
						{
							salida = EscribeLin(midi);
						}
						else
						{
								error = 1;
						}
					}
				}
			}
			else
			{
			    fprintf(stderr, "Error: can not open file %s\n", argv[2]);
				error = 1;
			}
		}
		else
		{
			error = 1;
		}
	}
	

	if(!error)
	{
		if(argc > 4 )
		{
			if(strcmp(argv[3], "-o") == 0 )
			{
				//write file
	
				fout = fopen(argv[4], "w");
					
				if(fout)
				{
					fprintf(fout, "%s", salida);
						
					fclose(fout);
	
					printf("File '%s' generated.\n", argv[4]);
				}
				else
				{
					printf("file '%s' could not be opened.\n", argv[4]);
				}
			}
			else
			{
				error = 1;
			}
		}
		else
		{
			printf("%s\n", salida);
		}
	}
	
	if(error)
	{
		printf("Usage: %s -{r|x|l} file [-o fileoutput] \n\
try --help for more information\n", argv[0]);
	}

	if(salida != NULL)
	{
		free(salida);
	}
	
	return 0;
}
