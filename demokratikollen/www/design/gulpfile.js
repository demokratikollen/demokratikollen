var gulp = require('gulp'),
    conc = require('gulp-concat'),
    uglify = require('gulp-uglify'),
    rename = require('gulp-rename'),
    sass = require('gulp-ruby-sass');

var work_dir = '/home/vagrant/demokratikollen/www/design/';
var dist_dir = '/home/vagrant/demokratikollen/www/app/static/';

var bs_assets_dir = 'bower_components/bootstrap-sass-official/assets/';
var bs_styles_dir = work_dir+bs_assets_dir+'stylesheets/'
var bs_scripts_dir = work_dir+bs_assets_dir+'javascripts/'

var bs_js_deps = [bs_scripts_dir+'bootstrap/collapse.js']
// var bs_js_deps = [bs_scripts_dir+'bootstrap.js']

var sass_files = work_dir+'sass/*.scss'
var js_files = work_dir+'javascripts/*.js'
var css_dist = dist_dir+'css'
var js_dist = dist_dir+'js'

gulp.task('styles', function () {
    console.log('Sassing...');
    gulp.src(sass_files)
        .pipe(sass({loadPath: bs_styles_dir, style: 'compressed'}))
        .pipe(gulp.dest(css_dist));
});

gulp.task('scripts', function () {
    gulp.src(bs_js_deps)
        .pipe(conc('dependencies.js'))
        .pipe(gulp.dest(js_dist))
        .pipe(uglify())
        .pipe(rename({suffix: '.min'}))
        .pipe(gulp.dest(js_dist));
});

gulp.task('watch', function() {
    console.log('Built-in watch')
    gulp.watch(sass_files, ['styles']);
    gulp.watch(js_files, ['scripts']);
});

gulp.task('default',['styles','scripts'])