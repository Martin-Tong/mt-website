var qrcode = new QRCode({
  content: location.href,
  container: "svg-viewbox", //Responsive use
  join: true //Crisp rendering and 4-5x reduced file size
});
var svg = qrcode.svg();
document.getElementById("qrcode_container").innerHTML = svg;