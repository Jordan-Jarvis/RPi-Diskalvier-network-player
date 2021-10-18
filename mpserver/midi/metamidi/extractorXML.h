/*
Copyright (c) 2009 Jose M. Inesta <inesta@dlsi.ua.es>
Copyright (c) 2009 Pedro J. Ponce de Leon <pierre@dlsi.ua.es>
Copyright (c) 2009 Carlos Perez Sancho <cperez@dlsi.ua.es>
Copyright (c) 2009 Antonio Pertusa Ibanez <pertusa@dlsi.ua.es>
Copyright (c) 2009 David Rizo Valero <drizo@dlsi.ua.es>
Copyright (c) 2009 Tomas Perez Garcia <tperez@dlsi.ua.es>
Copyright (c) 2009 Universitat d'Alacant
*/

#ifndef EXTRACTORXML_H_
#define EXTRACTORXML_H_

#include <stdio.h>
#include <math.h>
#include <string.h>
#include <stdarg.h>
#include <stdlib.h>
#include "tmidi.h"

char* getComments(char* texto);
char* getTrack(TPista tp);
char* getTracks(TMidi tm);
char* getGlobal(TMidi tm);
char* getExternal(TMidi tm);
char* getMidiFile(TMidi tm);


#endif /*EXTRACTORXML_H_*/
