#!/usr/bin/perl

use strict;
use warnings FATAL => 'all';
use utf8;
use JSON;


sub saveFile {
    my ($filename, $data) = @_;
    if ($data) {
        my $mode = ">";

        if (not open OUT, "$mode$filename") {
            return 0;
        }

        #binmode OUT;
        binmode STDOUT, ":utf8";
        print OUT $data;
        close OUT;
        return 1;
    }
}

sub save_as_json {
    my($file_name, $data) = @_;
    print "SAVED as: '$file_name'\n";
    my $json = new JSON;
    $json = $json->pretty([1]);
    my $json_text = $json->encode($data);
    saveFile($file_name, $json_text);

}

sub load_json {
    my($file_name) = @_;
    print "LOAD JSON FROM: '$file_name'\n";
    my $json_str;
    my $data;

    local $/; #Enable 'slurp' mode
    open my $fh, "<", $file_name;
    $json_str = <$fh>;
    close $fh;

    $data = decode_json($json_str);
    return $data
}



my $num_args = $#ARGV + 1;
my $input_name = $ARGV[0];
my $file_name = $input_name;
my $output_name = $input_name;

if ($num_args == 0) {
    print "Usage:  json_repack <INPUT_JSON>\n";
}
else {
    $file_name = "$input_name.bak";
    print "existed file stored as '$file_name'\n";
    rename $input_name, $file_name;
    my $data = load_json($file_name);
    save_as_json($output_name, $data);
}