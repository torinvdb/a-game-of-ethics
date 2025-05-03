window.HELP_IMPROVE_VIDEOJS = false;


$(document).ready(function() {
    // Check for click events on the navbar burger icon

    var options = {
			slidesToScroll: 1,
			slidesToShow: 1,
			loop: true,
			infinite: true,
			autoplay: true,
			autoplaySpeed: 5000,
    }

		// Initialize all div with carousel class
    var carousels = bulmaCarousel.attach('.carousel', options);
	
    bulmaSlider.attach();

})

// Function to handle scenario card clicks
document.addEventListener('DOMContentLoaded', function() {
  // Set up event listeners for scenario card links
  const scenarioLinks = document.querySelectorAll('.game-selector .card-footer-item:not([disabled])');
  const gameContainer = document.getElementById('game-container');
  const gameFrame = document.getElementById('game-frame');
  
  scenarioLinks.forEach(link => {
    link.addEventListener('click', function(e) {
      e.preventDefault();
      const gameUrl = this.getAttribute('href');
      
      // Reset the iframe by clearing it first
      gameFrame.src = 'about:blank';
      
      // Small delay to ensure the iframe is fully reset
      setTimeout(() => {
        // Update the iframe source
        gameFrame.src = gameUrl;
        
        // Show the game container
        gameContainer.style.display = 'block';
        
        // Scroll to the game container
        gameContainer.scrollIntoView({ behavior: 'smooth' });
      }, 100);
    });
  });
});
