//handles the image switcher on the add race page so the picture matches the sport selected
const sportInput = document.getElementById('name');
const raceImg = document.getElementById('raceimg');
const raceLabel = document.getElementById('race-label');

//default pic shown before the user picks a sport
const defaultImg = '/static/images/Pic1.jpg';
const defaultLabel = 'Your Sport';

//maps each sport to its image
const sportMap = {
    'running':  '/static/images/Pic1.jpg',
    'swimming': '/static/images/Pic2.jpg',
    'cycling':  '/static/images/Pic4.jpg',
    'rowing': '/static/images/Pic9.jpg',
};

//runs whenever the user changes the sport dropdown
sportInput.addEventListener('change', function() {
    const typed = sportInput.value.toLowerCase().trim();
    const match = sportMap[typed];

    if (match) {
        raceImg.src = match;
        raceLabel.textContent = sportInput.value;
    } else if (typed === '') {
        raceImg.src = defaultImg;
        raceLabel.textContent = defaultLabel;
    }
});