#!/usr/bin/perl

#Copyright (c) 1997 The Regents of the University of California.
#All rights reserved.
#
#Permission to use, copy, modify, and distribute this software for any
#purpose, without fee, and without written agreement is hereby granted,
#provided that the above copyright notice and the following two
#paragraphs appear in all copies of this software.
#
#IN NO EVENT SHALL THE UNIVERSITY OF CALIFORNIA BE LIABLE TO ANY PARTY FOR
#DIRECT, INDIRECT, SPECIAL, INCIDENTAL, OR CONSEQUENTIAL DAMAGES ARISING OUT
#OF THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION, EVEN IF THE UNIVERSITY OF
#CALIFORNIA HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
#THE UNIVERSITY OF CALIFORNIA SPECIFICALLY DISCLAIMS ANY WARRANTIES,
#INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY
#AND FITNESS FOR A PARTICULAR PURPOSE.  THE SOFTWARE PROVIDED HEREUNDER IS
#ON AN "AS IS" BASIS, AND THE UNIVERSITY OF CALIFORNIA HAS NO OBLIGATION TO
#PROVIDE MAINTENANCE, SUPPORT, UPDATES, ENHANCEMENTS, OR MODIFICATIONS.
#
#
# STOP.  It should not be necessary to change anything below this line
# to use the script.
#
use IO::Socket;

#
# As of the date this script was written, the following languages were supported.  This script will work with 
# languages added later however.  Check the moss website for the full list of supported languages.
#
@languages = ("c", "cc", "java", "ml", "pascal", "ada", "lisp", "scheme", "haskell", "fortran", "ascii", "vhdl", "perl", "matlab", "python", "mips", "prolog", "spice", "vb", "csharp", "modula2", "a8086", "javascript", "plsql", "verilog");

$server = 'moss.stanford.edu';
$port = '7690';
$noreq = "Request not sent.";
$usage = "usage: moss [-x] [-l language] [-d] [-b basefile1] ... [-b basefilen] [-m #] [-c \"string\"] file1 file2 file3 ...";

#
# The userid is used to authenticate your queries to the server; don't change it!
#
$userid=302411304;

#
# Process the command line options.  This is done in a non-standard
# way to allow multiple -b's.
#
$opt_l = "c";   # default language is c
$opt_m = 10;
$opt_d = 0;
$opt_x = 0;
$opt_c = "";
$opt_n = 250;
$bindex = 0;    # this becomes non-zero if we have any base files

while (@ARGV && ($_ = $ARGV[0]) =~ /^-(.)(.*)/) {
    ($first,$rest) = ($1,$2);   
    
    shift(@ARGV);
    if ($first eq "d") {
        $opt_d = 1;
        next;
    }
    if ($first eq "b") {
        if($rest eq '') {
            die "No argument for option -b.\n" unless @ARGV;
            $rest = shift(@ARGV);
        }
        $opt_b[$bindex++] = $rest;
        next;
    }
    if ($first eq "l") {
        if ($rest eq '') {
            die "No argument for option -l.\n" unless @ARGV;
            $rest = shift(@ARGV);
        }
        $opt_l = $rest;
        next;
    }
    if ($first eq "m") {
        if($rest eq '') {
            die "No argument for option -m.\n" unless @ARGV;
            $rest = shift(@ARGV);
        }
        $opt_m = $rest;
        next;
    }
    if ($first eq "c") {
        if($rest eq '') {
            die "No argument for option -c.\n" unless @ARGV;
            $rest = shift(@ARGV);
        }
        $opt_c = $rest;
        next;
    }
    if ($first eq "n") {
        if($rest eq '') {
            die "No argument for option -n.\n" unless @ARGV;
            $rest = shift(@ARGV);
        }
        $opt_n = $rest;
        next;
    }
    if ($first eq "x") {
        $opt_x = 1;
        next;
    }
    #
    # Override the name of the server.  This is used for testing this script.
    #
    if ($first eq "s") {
        $server = shift(@ARGV);
        next;
    }
    #
    # Override the port.  This is used for testing this script.
    #
    if ($first eq "p") {
        $port = shift(@ARGV);
        next;
    }
    die "Unrecognized option -$first.  $usage\n"; 
}

#
# Check a bunch of things first to ensure that the
# script will be able to run to completion.
#

#
# Make sure all the argument files exist and are readable.
#
#print "Checking files . . . \n";
$i = 0;
while($i < $bindex)
{
    die "Base file $opt_b[$i] does not exist. $noreq\n" unless -e "$opt_b[$i]";
    die "Base file $opt_b[$i] is not readable. $noreq\n" unless -r "$opt_b[$i]";
    die "Base file $opt_b is not a text file. $noreq\n" unless -T "$opt_b[$i]";
    $i++;
}
foreach $file (@ARGV)
{
    die "File $file does not exist. $noreq\n" unless -e "$file";
    die "File $file is not readable. $noreq\n" unless -r "$file";
    die "File $file is not a text file. $noreq\n" unless -T "$file";
}

if ("@ARGV" eq '') {
    die "No files submitted.\n $usage";
}
#print "OK\n";

#
# Now the real processing begins.
#


$sock = new IO::Socket::INET (
                                  PeerAddr => $server,
                                  PeerPort => $port,
                                  Proto => 'tcp',
                                 );
die "Could not connect to server $server: $!\n" unless $sock;
$sock->autoflush(1);

sub read_from_server {
    $msg = <$sock>;
    print $msg;
}

sub upload_file {
    local ($file, $id, $lang) = @_;
#
# The stat function does not seem to give correct filesizes on windows, so
# we compute the size here via brute force.
#
    open(F,$file);
    $size = 0;
    while (<F>) {
        $size += length($_);
    }
    close(F);

    #print "Uploading $file ...";
    open(F,$file);
    $file =~s/\s/\_/g;    # replace blanks in filename with underscores
    print $sock "file $id $lang $size $file\n";
    while (<F>) {
        print $sock $_;
    }
    close(F);
    #print "done.\n";
}


print $sock "moss $userid\n";      # authenticate user
print $sock "directory $opt_d\n";
print $sock "X $opt_x\n";
print $sock "maxmatches $opt_m\n";
print $sock "show $opt_n\n";

#
# confirm that we have a supported languages
#
print $sock "language $opt_l\n";
$msg = <$sock>;
chop($msg);
if ($msg eq "no") {
    print $sock "end\n";
    die "Unrecognized language $opt_l.";
}


# upload any base files
$i = 0;
while($i < $bindex) {
    &upload_file($opt_b[$i++],0,$opt_l);
}

$setid = 1;
foreach $file (@ARGV) {
    &upload_file($file,$setid++,$opt_l); 
}

print $sock "query 0 $opt_c\n";
#print "Query submitted.  Waiting for the server's response.\n";
&read_from_server();
print $sock "end\n";
close($sock);