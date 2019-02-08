#!/usr/bin/perl

#
# Authentic Theme (https://github.com/authentic-theme/authentic-theme)
# Copyright Ilia Rostovtsev <programming@rostovtsev.io>
# Licensed under MIT (https://github.com/authentic-theme/authentic-theme/blob/master/LICENSE)
#
use strict;

use File::Basename;

our (%in, %gconfig, %miniserv, %tconfig, %text, $config_directory, $current_theme, %theme_text);

require(dirname(__FILE__) . "/authentic-lib.pm");

my %miniserv;
get_miniserv_config(\%miniserv);

my $charset = &get_charset();

# Check to add error handler
error_40x_handler();

our %theme_config = (settings($config_directory . "/$current_theme/settings-admin", 'settings_'),
                     settings($config_directory . "/$current_theme/settings-root",  'settings_'));

# Show pre-login text banner
if ($gconfig{'loginbanner'} &&
    get_env('http_cookie') !~ /banner=1/ &&
    !$in{'logout'}                       &&
    !$in{'failed'}                       &&
    !$in{'password'}                     &&
    !$in{'error'}                        &&
    $in{'initial'})
{

    print "Auth-type: auth-required=1\r\n";
    print "Set-Cookie: banner=1; path=/\r\n";
    &PrintHeader($charset);
    print '<!DOCTYPE HTML>', "\n";
    print '<html data-background-style="'
      .
      ( theme_night_mode() ? 'nightRider' :
          'gainsboro'
      ) .
      '" data-night-mode="' . theme_night_mode() . '" class="session_login pam_login">', "\n";
    embed_login_head();
    print '<body class="session_login pam_login" ' . $tconfig{'inbody'} . '>' . "\n";
    embed_overlay_prebody();
    print
'<div class="form-signin-banner container session_login pam_login alert alert-danger" data-dcontainer="1"><i class="fa fa-3x fa-exclamation-triangle"></i><br><br>'
      . "\n";
    my $url = $in{'page'};
    open(BANNER, $gconfig{'loginbanner'});

    while (<BANNER>) {
        s/LOGINURL/$url/g;
        print;
    }

    close(BANNER);
    &footer();
    return;
}

my $sec = lc(get_env('https')) eq 'on' ? "; secure" : "";
my $sidname = $miniserv{'sidname'} || "sid";
print "Auth-type: auth-required=1\r\n";
print "Set-Cookie: banner=0; path=/$sec\r\n"   if ($gconfig{'loginbanner'});
print "Set-Cookie: $sidname=x; path=/$sec\r\n" if ($in{'logout'});
print "Set-Cookie: redirect=1; path=/\r\n";
print "Set-Cookie: testing=1; path=/$sec\r\n";
&PrintHeader($charset);
print '<!DOCTYPE HTML>', "\n";
print '<html data-background-style="'
  .
  ( theme_night_mode() ? 'nightRider' :
      'gainsboro'
  ) .
  '" data-night-mode="' . theme_night_mode() . '" class="session_login pam_login">', "\n";
embed_login_head();
print '<body class="session_login pam_login" ' . $tconfig{'inbody'} . '>' . "\n";
embed_overlay_prebody();
print '<div class="container session_login pam_login" data-dcontainer="1">' . "\n";

if (defined($in{'failed'})) {

    print '<div class="alert alert-warning">' . "\n";
    print '<strong><i class ="fa fa-exclamation-triangle"></i> ' . $theme_text{'login_warning'} . '</strong><br />' . "\n";
    print '<span>' . $theme_text{'theme_xhred_session_failed'} . "</span>\n";
    print '</div>' . "\n";

} elsif ($in{'logout'}) {
    print '<div class="alert alert-success">' . "\n";
    print '<strong><i class ="fa fa-check"></i> ' . $theme_text{'login_success'} . '</strong><br />' . "\n";
    print '<span>' . $theme_text{'session_logout'} . "</span>\n";
    print '</div>' . "\n";
} elsif ($in{'timed_out'}) {
    print '<div class="alert alert-warning">' . "\n";
    print '<strong><i class ="fa fa fa-exclamation-triangle"></i> ' .
      $theme_text{'login_warning'} . '</strong><br />' . "\n";
    print '<span>' . &theme_text('session_timed_out', int($in{'timed_out'} / 60)) . "</span>\n";
    print '</div>' . "\n";
}
print "$text{'pam_prefix'}\n";
print '<form method="post" action="' . $gconfig{'webprefix'} .
  '/pam_login.cgi" class="form-signin session_login pam_login clearfix" role="form" onsubmit="spinner()">' . "\n";
print ui_hidden("cid", $in{'cid'});

print '<i class="wbm-webmin"></i><h2 class="form-signin-heading">
     <span>'
  . (&get_product_name() eq 'webmin' ? $theme_text{'theme_xhred_titles_wm'} :
       $theme_text{'theme_xhred_titles_um'}
  ) .
  '</span></h2>' . "\n";

# Process logo
embed_logo();

# Login message
my $host;
if ($gconfig{'realname'}) {
    $host = &get_system_hostname();
} else {
    $host = get_env('server_name');
    $host =~ s/:\d+//g;
    $host = &html_escape($host);
}

print '<p class="form-signin-paragraph">' . &theme_text('login_message') . '<strong> ' . $host . '</strong></p>' . "\n";
if (!$in{'password'}) {
    print '<div class="input-group form-group">' . "\n";
    print '<span class="input-group-addon"><i class="fa fa-fw fa-user"></i></span>' . "\n";
    print
'<input type="text" class="form-control session_login pam_login" name="answer" autocomplete="off" autocapitalize="none" placeholder="'
      . &theme_text('theme_xhred_login_user')
      . '" ' . ' autofocus>' . "\n";
    print '</div>' . "\n";
} else {

    print '<div class="input-group form-group">' . "\n";
    print '<span class="input-group-addon"><i class="fa fa-fw fa-lock"></i></span>' . "\n";
    print
      '<input type="password" class="form-control session_login pam_login" name="answer" autocomplete="off" placeholder="' .
      &theme_text('theme_xhred_login_pass') . '" autofocus>' . "\n";
    print '</div>' . "\n";
}

print '<div class="form-group form-signin-group">';
print '<button class="btn btn-primary" type="submit"><i class="fa fa-sign-in"></i>&nbsp;&nbsp;' .
  ($in{'password'} ? &theme_text('pam_login') : &theme_text('login_signin')) . '</button>' . "\n";
if (!$in{'password'}) {
    if ($text{'session_postfix'} =~ "href") {
        my $link = get_link($text{'session_postfix'}, 'ugly');
        print '<button onclick=\'window.open("' . $link->[0] . '", "' . $link->[1] .
'", "toolbar=no,menubar=no,scrollbars=no,resizable=yes,width=700,height=500");return false;\' class="btn btn-warning"><i class="fa fa-unlock"></i>&nbsp;&nbsp;'
          . &theme_text('login_reset')
          . '</button>' . "\n";
    }

} else {
    print '<button class="btn btn-default" type="submit" name="restart"><i class="fa fa-backup fa-1_25x"></i>&nbsp;&nbsp;' .
      &theme_text('pam_restart') . '</button>' . "\n";
}

print '</div>';
print '</form>' . "\n";
print "$text{'pam_postfix'}\n";
&footer();
