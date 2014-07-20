module.exports = function(grunt) {
  grunt.initConfig({
    pkg: grunt.file.readJSON('package.json'),
    uglify: {
      options: {
        mangle: false
      },
      deps: {
        files: [{
          expand: true,
          cwd: 'app/lib',
          src: '**/*.js',
          dest: 'app/lib'
        }]
      },
      app: {
        files: [{
          expand: true,
          cwd: 'app/js',
          src: '**/*.js',
          dest: 'app/lib',
        }]
      }
    },
    bower: {
      install: {
        options: {
          targetDir: "app/lib",
        }
      }
    },
    watch: {
      bower: {
        files: ['bower.js'],
        tasks: ['bower']
      },
      deps: {
        files: ["bower_components/**/*"],
        tasks: ['bower', 'uglify:deps']
      },
      scripts: {
        files: ['app/js/**/*.js', 'app/js/*.js'],
        tasks: ['uglify:app'],
      }
    }
  });

  grunt.loadNpmTasks('grunt-bower-task');
  grunt.loadNpmTasks('grunt-contrib-uglify');
  grunt.loadNpmTasks('grunt-contrib-watch');
  grunt.registerTask('default', ['bower', 'uglify:deps', 'uglify:app']);

};
