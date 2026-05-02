const sportInput = document.getElementById('sport');
const raceImg = document.getElementById('raceimg');
const raceLabel = document.getElementById('race-label');

const defaultImg = '/static/images/Pic1.jpg';
const defaultLabel = 'Your Sport';

const sportMap = {
    'running':  '/static/images/Pic1.jpg',
    'swimming': '/static/images/Pic2.jpg',
    'cycling':  '/static/images/Pic4.jpg',
    'rowing': '/static/images/Pic9.jpg',
};

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