
// transform each link to an mp3 in a playable item

const audiolinks = document.querySelectorAll("a[href$=mp3]");

audiolinks.forEach(link => {
  const audio = document.createElement("audio");
  audio.src = link.href;
  link.appendChild(audio);
  link.addEventListener('click', (e) => {
    e.preventDefault();
    if(link.classList.contains('playing')){
      audio.pause();
    } else {
      audio.play();
    }
    link.classList.toggle('playing');
  })
});