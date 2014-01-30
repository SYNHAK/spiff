module.exports = function(grunt) {
  grunt.initConfig({
    bower: {
      install: {
      }
    }
  });

  grunt.loadNpmTasks('grunt-bower-task');
  grunt.registerTask('default', ['bower']);

};
