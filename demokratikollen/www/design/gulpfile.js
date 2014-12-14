/* ========================================================================
 * Setup
 * ======================================================================== */
var gulp = require('gulp'),
    concatenate = require('gulp-concat'),
    uglify = require('gulp-uglify'),
    sourcemaps = require('gulp-sourcemaps'),
    minifyCss = require('gulp-minify-css'),
    rename = require('gulp-rename'),
    sass = require('gulp-ruby-sass'),
    gulpFilter = require('gulp-filter'),
    plumber = require('gulp-plumber'),
    gulpOrder = require('gulp-order');

var work_dir = '/home/vagrant/demokratikollen/www/design/',
    dist_dir = '/home/vagrant/demokratikollen/www/app/static/';

/* ========================================================================
 * Dependencies
 * ======================================================================== */
var bs_assets_dir = 'bower_components/bootstrap-sass-official/assets/',
    bs_styles_dir = work_dir+bs_assets_dir+'stylesheets/',
    bs_scripts_dir = work_dir+bs_assets_dir+'javascripts/';

var jqueryUiDir = 'bower_components/jqueryui/',
    jqueryUiThemeDir = jqueryUiDir+'themes/smoothness/',
    jqueryUiSliderPipsDir = 'bower_components/jquery-ui-slider-pips/dist/';

var js_deps = [
    // Main libraries
    'bower_components/jquery/dist/jquery.js',
    'bower_components/d3/d3.js',
    'bower_components/d3-tip/index.js',
    // jQueryUI components
    jqueryUiDir+'ui/core.js',
    jqueryUiDir+'ui/widget.js',
    jqueryUiDir+'ui/mouse.js',
    jqueryUiDir+'ui/slider.js',
    jqueryUiSliderPipsDir+'jquery-ui-slider-pips.js',
    // Bootstrap plugins
    bs_scripts_dir+'bootstrap/transition.js',
    bs_scripts_dir+'bootstrap/collapse.js',
    // Other dependencies
    'bower_components/topojson/topojson.js',
    // Typeahead
    // 'bower_components/typeahead.js/dist/typeahead.bundle.js',
    // Fuse.js
    'bower_components/fuse.js/src/fuse.js'
];

var style_deps = [
    jqueryUiThemeDir+'jquery-ui.css',
    jqueryUiSliderPipsDir+'jquery-ui-slider-pips.css'
];

/* ========================================================================
 * Paths for collection/compilation and distribution
 * ======================================================================== */
var sass_files = work_dir+'sass/*.scss',
    js_files = work_dir+'js/*.js',
    css_dist = dist_dir+'css/',
    js_dist = dist_dir+'js/';

/* ========================================================================
 * Copying tasks
 * ======================================================================== */
gulp.task('copy-css-images', function() {
    return gulp.src(jqueryUiThemeDir+'images/*')
        .pipe(gulp.dest(css_dist+'images/'));
});
gulp.task('copy-fonts', function() {
    return gulp.src(bs_assets_dir+'fonts/**/*')
        .pipe(gulp.dest(dist_dir+'fonts/'));
});

gulp.task('copy',['copy-css-images','copy-fonts']);

/* ========================================================================
 * Compilation tasks
 * ======================================================================== */
gulp.task('styles', function () {
    var filter = gulpFilter('**/*.css');
    return gulp.src(sass_files)
        .pipe(plumber())
        .pipe(sass({loadPath: bs_styles_dir, style:'compressed'}))
        .pipe(filter)
        .pipe(rename({suffix: '.min'}))
        .pipe(filter.restore())
        .pipe(gulp.dest(css_dist));
});

gulp.task('scripts', function () {
    return gulp.src(js_files)
        .pipe(gulpOrder([
            "demokratikollen.js", // This one should be first to establish the namespace
            "utils.js", // May be used by others
            "*.js"
            ], { base: work_dir + "js/"}))
        .pipe(plumber())
        .pipe(sourcemaps.init({loadMaps: true}))
        .pipe(concatenate('scripts.js'))
        .pipe(uglify())
        .pipe(rename({suffix: '.min'}))
        .pipe(sourcemaps.write('../js'))
        .pipe(gulp.dest(js_dist));
});


/* ========================================================================
 * Dependencies concat/minification
 * ======================================================================== */
gulp.task('style-deps', function () {
    return gulp.src(style_deps)
        .pipe(plumber())
        .pipe(sourcemaps.init({loadMaps: true}))
        .pipe(concatenate('dependencies.css'))
        .pipe(minifyCss())
        .pipe(rename({suffix: '.min'}))
        .pipe(sourcemaps.write('../css'))
        .pipe(gulp.dest(css_dist));
});

gulp.task('script-deps', function () {
    return gulp.src(js_deps)
        .pipe(plumber())
        .pipe(sourcemaps.init({loadMaps: true}))
        .pipe(concatenate('dependencies.js'))
        .pipe(uglify())
        .pipe(rename({suffix: '.min'}))
        .pipe(sourcemaps.write('../js'))
        .pipe(gulp.dest(js_dist));
});

/* ========================================================================
 * Watch and combined tasks
 * ======================================================================== */
gulp.task('watch', function() {
    gulp.watch(sass_files, ['styles']);
    gulp.watch(js_files, ['scripts'])
});

gulp.task('all',['copy','styles','style-deps','script-deps']);
gulp.task('default',['styles','scripts','watch']);
gulp.task('dependencies',['style-deps','script-deps']);
