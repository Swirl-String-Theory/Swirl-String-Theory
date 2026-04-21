# LATEXMK_ROOT_SWIRL
# SwirlStringTheory — unified LaTeX layout
#   Final PDF -> <repo>/out
#   Auxiliary files -> <repo>/auxil
#
# When this file is the entry rc (cwd = repo root), directories are set below.
# Subfolder stubs load this file via upward search.

use Cwd qw(abs_path);
use File::Basename qw(dirname);
use File::Spec;

sub _swirl_latexmk_project_root {
  my $dir = abs_path( $ENV{PWD} || '.' );
  for ( 0 .. 24 ) {
    my $candidate = File::Spec->catfile( $dir, 'latexmkrc' );
    if ( -e $candidate ) {
      open my $fh, '<', $candidate or next;
      my $head = do { local $/; <$fh> };
      close $fh;
      if ( defined $head && $head =~ /^#\s*LATEXMK_ROOT_SWIRL/m ) {
        return $dir;
      }
    }
    my $parent = dirname($dir);
    last if $parent eq $dir;
    $dir = $parent;
  }
  return abs_path('.');
}

my $_repo = _swirl_latexmk_project_root();
$out_dir = File::Spec->catdir( $_repo, 'out' );
$aux_dir = File::Spec->catdir( $_repo, 'auxil' );
