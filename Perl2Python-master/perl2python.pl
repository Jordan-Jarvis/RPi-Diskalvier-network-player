#!/usr/bin/perl -w

use strict;

my $whitespaceCounter = 0; #global variable? Its outside the loop...

while (my $line = <>) {

	#NOTE: Deal with semicolons on a line by line basis

# translate #! line 
	if ($line =~ /^#!/ && $. == 1) {
		print "#!/usr/bin/python2.7 -u\n";

 # Blank & comment lines (unchanged)
	} elsif ($line =~ /^\s*#/ || $line =~ /^\s*$/) {
		print $line;

 #print statement with newline
	} elsif ($line =~ /^\s*print\s*"(.*)\\n"[\s;]*$/) {
		my $printInput = $1;
		if($printInput =~ /ARGV\[(.*)\]$/) { #that variable is ARGV[]
			&whitespacePrinter($whitespaceCounter);
			my $location = $1;
			$location =~ s/\$//;
			print "print sys.argv[$location + 1]\n"
		} elsif ($printInput =~ /^(.*)\s*\$(.*)*$/) { #there is ONE $variable
			$printInput =~ s/\$//; #removes variable signs
			&whitespacePrinter($whitespaceCounter);
			print "print $printInput\n";
		} elsif ($printInput =~ /^(.*)\s*\@(.*)*$/) { #there is ONE @variable
			$printInput =~ s/\@//;
			&whitespacePrinter($whitespaceCounter);
			print "print $printInput\n";
		} else { #there is no variable (or many, which currently kill everything)
			&whitespacePrinter($whitespaceCounter);
			print "print \"$printInput\"\n";
		}

#print statment with no newline
	} elsif ($line =~ /^\s*print\s*"(.*)"[\s;]*$/) { 
		my $printInput = $1;
		if ($printInput =~ /^\s*print\s*\$\_\s*;$/) { #special case for $_ (IN THE CASE OF PRINTING FROM THE COMMAND LINE?) 
			&whitespacePrinter($whitespaceCounter);		
			print "print line\n";
		} elsif ($printInput =~ /^(.*)\s*\$(.*)*$/) { #there is ONE variable
			&whitespacePrinter($whitespaceCounter);			
			$printInput =~ s/\$//; #removes variable signs
			$printInput =~ s/\@//;
			print "sys.stdout.write($printInput)\n";
		} else { #there is no variable (or many, which currently kill everything)
			&whitespacePrinter($whitespaceCounter);
			print "sys.stdout.write(\"$printInput\")\n";
		}

#break/continue	
	} elsif ($line =~ /^\s*last;$/) {
		&whitespacePrinter($whitespaceCounter);
		print "break\n";

	} elsif ($line =~ /^\s*next;$/) {
		&whitespacePrinter($whitespaceCounter);
		print "continue\n";

#looping through every line in a FILE 
	} elsif ($line =~ /^\s*while\s*(.*)\<\>(.*)\s*(.*)\s*$/) {
		&whitespacePrinter($whitespaceCounter);	
		print "import fileinput\n";
		&whitespacePrinter($whitespaceCounter);	
		print "for line in fileinput.input():\n"	

#looping through STDIN (while loop)
	} elsif ($line =~ /^\s*while\s*(.*)\<STDIN\>(.*)\s*(.*)\s*$/) {
		&whitespacePrinter($whitespaceCounter);
		print "import sys\n";
		&whitespacePrinter($whitespaceCounter);
		print "for line in sys.stdin:\n"; 

#chomp from STDIN
	} elsif ($line =~ /^\s*chomp\s*\$(.*)\s*;$/) {
		&whitespacePrinter($whitespaceCounter);	
		print "$1 = sys.stdin.readlines()\n"

#split
	} elsif ($line =~ /^\s*(.*)\s*=\s*split\(\/(.*)\/,\s*\$(.*)\)\s*;/) {
		my $string = $3;
		my $delineator = $2;
		my $assignmentVariable = $1;
		&whitespacePrinter($whitespaceCounter);
		print "$assignmentVariable = $string.split(\"$delineator\")\n";

#join
	} elsif ($line =~ /^\s*(.*)\s*=\s*join\(\'(.*)\'\,\s*(.*)\)\s*;$/) {
		my $assignmentVariable = $1;
		my $string = $3;
		my $delineator = $2;
		&whitespacePrinter($whitespaceCounter);
		print "$assignmentVariable = '$delineator'.join([$string])";

#arithmetic operations
	} elsif ($line =~ /^\s*[^\s]*\s*=(.*);$/) {
		if ($line =~ /^\s*\@(.*)\s*=\s*(.*);$/) {#arrays are dealt with seperately
			next;
		} else {
			&whitespacePrinter($whitespaceCounter);
			&arithmeticLines($line);
		}

# ++ and --
	} elsif ($line =~ /^\s*(.*)\s*\+\+(.*);$/) { 
		# change ++ and -- to python equivalents
		&whitespacePrinter($whitespaceCounter);
		my $plusPlus = $1;
		$plusPlus =~ s/\$//;
		print "$plusPlus +=1\n";
	} elsif ($line =~ /^\s*(.*)\s*\-\-(.*);$/) {
		&whitespacePrinter($whitespaceCounter);
		my $minusMinus = $1;
		$minusMinus =~ s/\$//;
		print "$minusMinus -= 1\n";

#for loops (If in C style then no direct comparison)?
#foreach (with ARGV) (super specific, could do with broadening in scope)
	} elsif ($line =~ /^\s*foreach\s*\$(.*)\s*\((.*)\)\s*{\s*$/) {
		#foreach $i (0..$#ARGV) becomes for i in xrange (len(sys.argv) - 1):
		my $variableName = $1;
		&whitespacePrinter($whitespaceCounter);
		print "for $variableName in xrange (len(sys.argv) - 1):\n";

#while loops
	} elsif ($line =~ /^\s*(.*)\s*while\s*\((.*)\)(.*)\s*$/) {
		if ($line =~ /^\s*(.*)\s*while\s*\((.*)\s*\<STDIN\>\s*\)(.*)\s*$/) { #stdin   
			&whitespacePrinter($whitespaceCounter);		
			print "for line in sys.stdin:";
		} else {
			my $whileCondition = $2;
			&whitespacePrinter($whitespaceCounter);		
			print "while ";
			&arithmeticLines($whileCondition);
			print ":\n";
			$whitespaceCounter ++;
		}

# elsif 
	} elsif ($line =~ /^\s*(.*)\s*elsif\s*\((.*)\)(.*)\s*$/) {
		#remember to remove } if present
		#becomes elif
		my $elsifCondition = $2;
		&whitespacePrinter($whitespaceCounter-1);
		print "elif ";					#so, so frustratingly messy :/
		&arithmeticLines($elsifCondition);
		print ":\n";

#if statements
	} elsif ($line =~ /^\s*(.*)\s*if\s*\((.*)\)(.*)\s*$/) {
		my $ifCondition = $2;
		&whitespacePrinter($whitespaceCounter);
		print "if ";					#ugh this is messy :/
		&arithmeticLines($ifCondition);
		print ":\n";
		$whitespaceCounter ++;

#else
	} elsif ($line =~ /^\s*(.*)\s*else\s*(.*)\s*$/) {
		#remember to remove } if present
		&whitespacePrinter($whitespaceCounter-1);
		print "else:\n";;

#end curly brace needs removal
	} elsif ($line =~ /^\s*}\s*$/) {
		$line =~ s/\}/ /;
		$whitespaceCounter --;


#ARRAY HANDLING
#array conversion
	}elsif ($line =~ /^\s*(.*)\s*\@(.*)\s*(.*)\s*;$/) { #array in the line	
		my $arrayName = $2; 
		if (/^\s*(.*)\s*\@(.*)\s*=\s*((.*))\s*;$/) { #declaring the array
			$line =~ s/\@//;
			$line =~ s/\(/\[/;
			$line =~ s/\)/\]/;
			$line =~ s/\"/\'/g;
			$line =~ s/\;//;
			print "$line";
		} else { #accessing the array
			#  $arrayName[0 or whatever];
			$line =~ s/\@//;
			$line =~ s/\;//;
			print "$line";
		}
#push
	} elsif ($line =~ /^\s*push\s*\@(.*)\,\s*(.*)\s*;$/) {
		&whitespacePrinter($whitespaceCounter);
		print "$1.push($2)\n";

#pop
	} elsif ($line =~ /^\s*pop\s*\@(.*);$/) {
		&whitespacePrinter($whitespaceCounter);
		print "$1.pop\n";

#unshift
	} elsif ($line =~ /^\s*unshift\s*\@(.*)\,\s*(.*)\s*;$/) {
		&whitespacePrinter($whitespaceCounter);
		print "$1.unshift($2)\n";

#pop
	} elsif ($line =~ /^\s*shift\s*\@(.*);$/) {
		&whitespacePrinter($whitespaceCounter);
		print "$1.shift\n";


#concatenation with . (both dont add spaces by default yay) (with + is the same)
#	} elsif ($line =~ /^\s*(.*)\s*\.\s*(.*)\s*;$/) { #untested match
#		$line =~ s/\./\+/;
#		print $line;

#substitution s/// (UNTESTED)
	#    $line =~ s/[aeiou]//g; becomes     line = re.sub(r'[aeiou]', '', line)
#	} elsif ($line =~ /^\s*\$(.*)\s*(.*)\s*s\/(.*)\/(.*)\/(.*);$/) {
#		my $variableName = $1;
#		my $replaced = $3;
#		my $replacedWith = $4;
#		print "$variableName = re.sub(r'$3', '$4', $variableName)"

# Lines we can't translate are turned into comments
	} else { 
		print "#$line\n";
	}

}
sub arithmeticLines { 

	# $#
	$_[0] =~ s/\$\#ARGV/len\(sys\.argv\)/;

	#removes $ before variables
	$_[0] =~ s/\$//g;
	$_[0] =~ s/\@//g;

	#stdin
	$_[0] =~ s/\<STDIN\>/float\(sys\.stdin\.readline\(\)\)/;

	#and/or/not
	$_[0] =~ s/\&\&/and /g;
	$_[0] =~ s/\|\|/or /g;
	$_[0] =~ s/!\s/not /g;

	#comparison operators that dont exist in Python replaced with those that do
	$_[0] =~ s/ eq / == /g;
	$_[0] =~ s/ ne / != /g;
	$_[0] =~ s/ gt / > /g;
	$_[0] =~ s/ lt / < /g;
	$_[0] =~ s/ ge / >= /g;
	$_[0] =~ s/ le / <= /g;	

	#division
	$_[0] =~ s/\//\/\//g;

	#remove that semicolon
	$_[0] =~ s/\;//;
	print $_[0];
}

sub whitespacePrinter {
	my $whitespace = $_[0];
	for (my $x = 0; $x < $whitespace; $x ++) {
		print '   ';
	}
}


