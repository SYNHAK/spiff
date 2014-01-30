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
          cwd: 'build/lib/',
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
          targetDir: "build/lib",
          cleanTargetDir: true
        }
      }
    }
  });

  grunt.loadNpmTasks('grunt-bower-task');
  grunt.loadNpmTasks('grunt-contrib-uglify');
  grunt.registerTask('default', ['bower', 'uglify:deps', 'uglify:app']);

};
