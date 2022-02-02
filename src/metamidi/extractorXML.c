/*
Copyright (c) 2009 Jose M. Inesta <inesta@dlsi.ua.es>
Copyright (c) 2009 Pedro J. Ponce de Leon <pierre@dlsi.ua.es>
Copyright (c) 2009 Carlos Perez Sancho <cperez@dlsi.ua.es>
Copyright (c) 2009 Antonio Pertusa Ibanez <pertusa@dlsi.ua.es>
Copyright (c) 2009 David Rizo Valero <drizo@dlsi.ua.es>
Copyright (c) 2009 Tomas Perez Garcia <tperez@dlsi.ua.es>
Copyright (c) 2009 Universitat d'Alacant
*/


#include "extractorXML.h"
#include "define.h" 

char*
getComments(char* texto)
{
	char* comments;

	comments = strdup("");
	comments = concat(comments, "<comments>", cEOA);

	comments = concat(comments, texto, cEOA);
	comments = concat(comments, "</comments>\n", cEOA);

	return comments;
}

char*
getTrack(TPista tp)
{
	char* track;
	char *aux, *aux2;

	track = strdup("");	
	aux = (char*)malloc(sizeof(char)*500);
	
	track = concat(track, "<track ", cEOA);

	//metaeventtext
	aux2 = limpiarComillas(tp.descriptores.texto);
	track = concat(track, " metaeventtext=\"", aux2, "\"", cEOA);
	
	//chanel
	sprintf(aux, "%d", 	tp.descriptores.canal);
	track = concat(track, " channel=\"", aux, "\"", cEOA);
	
	//duration
	sprintf(aux, "%d", tp.descriptores.duracion);
	track = concat(track, " duration=\"", aux, "\"", cEOA);

	//durationRate
	sprintf(aux, "%.*f", NDEC, tp.descriptores.d_absoluta);
	track = concat(track, " durationRate=\"", aux, "\"", cEOA);

	//occupation
	sprintf(aux, "%d", tp.descriptores.d_sonido);
	track = concat(track, " occupation=\"", aux, "\"", cEOA);
	
	//occupationRate
	sprintf(aux, "%.*f", NDEC, tp.descriptores.sonido);
	track = concat(track, " occupationRate=\"", aux, "\"", cEOA);

	//polyphonyRate
	sprintf(aux, "%.*f", NDEC, tp.descriptores.polifonica);
	track = concat(track, " polyphonyDurationRate=\"", aux, "\"", cEOA);

	//maxSimultaneousNotes
	sprintf(aux, "%d", tp.descriptores.maxPolyphony);
	track = concat(track, " maxPolyphony=\"", aux, "\"", cEOA);

	//avgSimultaneousNotes
	sprintf(aux, "%.*f", NDEC, tp.descriptores.avgPolyphony);
	track = concat(track, " avgPolyphony=\"", aux, "\"", cEOA);
	
	//low pitch
	sprintf(aux, "%d", tp.descriptores.nota_baja);
	track = concat(track, " lowpitch=\"", aux, "\"", cEOA);
	
	//high pitch
	sprintf(aux, "%d", tp.descriptores.nota_alta);
	track = concat(track, " highpitch=\"", aux, "\"", cEOA);

	//modulations
	sprintf(aux, "%d", tp.descriptores.n_msgModulacion);
	track = concat(track, " modulations=\"", aux, "\"", cEOA);
	
	//afterTouches
	sprintf(aux, "%d", tp.descriptores.n_msgPostPul);
	track = concat(track, " afterTouches=\"", aux, "\"", cEOA);

	//pitchBends
	sprintf(aux, "%d", tp.descriptores.n_msgAltura);
	track = concat(track, " pitchBends=\"", aux, "\"", cEOA);

	//programChanges
	//sprintf(aux, "%d", tp.descriptores.n_cambiosPrograma);
	track = concat(track, " programChanges=\"", tp.descriptores.cambiosPrograma, "\"", cEOA);

	track = concat(track, ">\n", cEOA);
	
	free(aux);
	aux = NULL;

	//comments
	aux = getComments("");
	track = concat(track, aux, cEOA);

	aux = NULL;

	track = concat(track, "</track>\n", cEOA);
	
	return track;
}

char*
getTracks(TMidi tm)
{
	int i;
	char* tracks;
	char *aux;

	tracks = strdup("");	
	tracks = concat(tracks, "<tracks>\n", cEOA);

	for(i=0; i<tm.descriptores.numpistas; i++)
	{
		aux = getTrack(tm.pistas[i]);
		tracks = concat(tracks, aux, cEOA);
	}

	tracks = concat(tracks, "</tracks>\n", cEOA);
	
	return tracks;
}

char*
getGlobal(TMidi tm)
{
	char *global, *aux ,*aux2;
	float valor;
	
	global = strdup("");
	aux = (char*)malloc(sizeof(char)*500);
	
	global = concat(global, "<global ", cEOA);
	 
	//metaeventtext
	aux2 = limpiarComillas(tm.descriptores.texto);
	global = concat(global, " metaeventtext=\"", aux2, "\"", cEOA);
	
	//tempo
	sprintf(aux, "%.*f", NDEC, tm.descriptores.tempo);
	global = concat(global, " tempo=\"", aux, "\"", cEOA);

	//tempoChanges
	sprintf(aux, "%d", tm.descriptores.c_tempo);
	global = concat(global, " tempoChanges=\"", aux, "\"", cEOA);

	//meter
	//sprintf(aux, "%d/%d", tm.descriptores.num_compas, tm.descriptores.den_compas);
	//global = concat(global, " meter=\"", aux, "\"", cEOA);
	global = concat(global, " meter=\"", tm.descriptores.compases, "\"", cEOA);

	//meterChanges
	sprintf(aux, "%d", tm.descriptores.c_metrica);
	global = concat(global, " meterChanges=\"", aux, "\"", cEOA);

	//keySignature
	sprintf(aux, "%s", tm.descriptores.key);
	global = concat(global, " key=\"", aux, "\"", cEOA);

	//keyChanges
	sprintf(aux, "%d", tm.descriptores.c_tono);
	global = concat(global, " keyChanges=\"", aux, "\"", cEOA);

	//instruments
	global = concat(global, " instruments=\"", tm.descriptores.instrumentos, "\"", cEOA);

  	//percussion
  	global = concat(global, " percussion=\"", tm.descriptores.percusion, "\"", cEOA );

	//duration
	valor = tm.descriptores.duracion;
	sprintf(aux, "%.*f", NDEC, valor);
	global = concat(global, " duration=\"", aux, "\"", cEOA);

	//hasSysEx
	sprintf(aux, "%d", tm.descriptores.hasSysEx);
	global = concat(global, " hasSysEx=\"", aux, "\"", cEOA);

	global = concat(global, ">\n", cEOA);

	free(aux);
	aux = NULL;
	
	//comments
	aux = getComments("");
	global = concat(global, aux, cEOA);

	aux = NULL;

	global = concat(global, "</global>\n", cEOA);

	return global;
}

char*
getExternal(TMidi tm)
{
	char* external;
	char* aux;

	external = strdup("");	
	aux = (char*)malloc(sizeof(char)*20);
	aux[0] = '\0';

	external = concat(external, "<external ", cEOA);

	//name
	external = concat(external, " name=\"", limpiarComillas(tm.descriptores.path), "\"", cEOA);
	
	//size
	sprintf ( aux, "%ld",  tm.descriptores.bytes);
	external = concat(external, " size=\"", aux, "\"", cEOA);

	//midiformat
	sprintf ( aux, "%d",  tm.descriptores.formato);
	external = concat(external, " midiformat=\"", aux, "\"", cEOA);

	//numtracks
	sprintf ( aux, "%d",  tm.descriptores.numpistas);
	external = concat(external, " numtracks=\"", aux, "\"", cEOA);

  	//resolution
	sprintf(aux, "%d", tm.descriptores.division);
	external = concat(external, " resolution=\"", aux, "\"", cEOA);

	//cerrar tag external
	external = concat(external, ">\n", cEOA);

	//comments
	aux = getComments("");
	external = concat(external, aux, cEOA);

	external = concat(external, "</external>\n", cEOA);

	aux = NULL;
	return external;
}

char*
getMidiFile(TMidi tm)
{
	char* midifile;
	char* aux;
	
	midifile = strdup("");

	midifile = concat(midifile, "<?xml version=\"1.0\" encoding=\"ISO-8859-1\"?>\n", cEOA);
	midifile = concat(midifile, "<!DOCTYPE midifile SYSTEM \"metamidi.dtd\">\n", cEOA);
	midifile = concat(midifile, "<midifile>\n", cEOA);

	
	//external
	aux = getExternal(tm);
	midifile = concat(midifile, aux, cEOA);
	
	//global
	aux = getGlobal(tm);
	midifile = concat(midifile, aux, cEOA);
	
	//traks
	aux = getTracks(tm);
	midifile = concat(midifile, aux, cEOA);

	midifile = concat(midifile, "</midifile>\n", cEOA);

	return midifile;
}

