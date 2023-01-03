function getCanvas() {
    return {
        canvas: document.getElementById("canvas"),
        context: this.canvas.getContext("2d")
    }
}

function monoring(context, x, y, radius, width, ringColor, circleColor, checkLineColor, startAngle = Math.PI / 2) {
    this.radius = radius;
    this.width = width;
    this.x = x;
    this.y = y;
    this.ringColor = ringColor;
    this.circleColor = circleColor;
    this.checkLineColor = checkLineColor;
    
    this.startAngle = startAngle;
    this.angle = startAngle;

    this.draw = function() {
        context.beginPath();
        
        context.arc(this.x, this.y, this.radius, 0, 2 * Math.PI, false);
        context.lineWidth = this.width;
        context.strokeStyle = this.ringColor;
        context.stroke();

        const outerRadius = this.radius + this.width/2;
        const innerRadius = this.radius - this.width/2;
        const cosStartAngle = Math.cos(-this.startAngle);
        const sinStartAngle = Math.sin(-this.startAngle);
        context.beginPath();
        context.moveTo(outerRadius * cosStartAngle + this.x, outerRadius * sinStartAngle + this.y);
        context.lineTo(innerRadius * cosStartAngle + this.x, innerRadius * sinStartAngle + this.y);
        context.strokeStyle = this.checkLineColor;
        context.lineWidth = 5;
        context.stroke();

        context.beginPath();
        context.arc(this.radius*Math.cos(-this.angle) + this.x, this.radius*Math.sin(-this.angle) + this.y, this.width / 2, 0, 2 * Math.PI, false);
        context.fillStyle = this.circleColor;
        context.fill();

        context.endPath();
    }
}

function update() {
    monoring.angle += 2 * Math.PI / DT / 100;
    monoring.draw(); 
}

const {canvas, context} = getCanvas();
const CENTER_X = canvas.width / 2;
const CENTER_Y = canvas.height / 2;
const DT = 10;

var monoring = new monoring(context, CENTER_X, 3*CENTER_Y/4, 200, 25, 'green', 'red', 'black');

setInterval(update, 10);