function getCanvas() {
    return {
        canvas: document.getElementById("canvas"),
        context: this.canvas.getContext("2d")
    }
}
const {canvas, context} = getCanvas();

// -------------------------------------------------
// CONSTANTS
const PI = Math.PI;
const TWOPI = 2 * PI;
const CENTER_X = canvas.width / 2;
const CENTER_Y = canvas.height / 2;

const BACKGROUND_COLOR = "#ffffff";
const FONT_FAMILY = "system-ui";

const DT = 10; // time interval between frames

const HINT_KEY = "h";

// ------------------------------------------------


function getRandomAngle() {
    return Math.random() * TWOPI;
}

function getRandomBetween(min, max) {
    return Math.random() * (max - min) + min
}

function normalizeAngle(angle) {
    if (angle < 0) angle += TWOPI;
    return angle % TWOPI;
}

function toRange(value, oldRangeMin, oldRangeMax, newRangeMin, newRangeMax) {
    var newValue = (value - oldRangeMin) * (newRangeMax - newRangeMin) / (oldRangeMax - oldRangeMin) + newRangeMin;
    return Math.min(Math.max(newValue, newRangeMin) , newRangeMax);
}

function hexToRgb(hex) {
    var result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? {
      r: parseInt(result[1], 16),
      g: parseInt(result[2], 16),
      b: parseInt(result[3], 16)
    } : null;
}

function lerp(start, end, amount){
    return (1-amount)*start+amount*end
}

function getRGBAString(hexColor, alpha) {
    var rgb = hexToRgb(hexColor);
    return `rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, ${alpha})`;
}

class Monoring
{
    constructor(
    context,    // canvas context
    key,        // keyboard key for current monoring
    x, y,       // coordinates of center of ring
    radius, width,
    ringColor, circleColor, checkLineColor = '#333333', 
    startAngle=PI/2, angularSpeed=0.01, 
    checkLineOffset=15, checkLineWidth=10,
    circleShadowBlur=7, circleShadowRadius=5, circleWidthOffset=-5,
    fontColor="#333333", fontSize=10,
    lastAccuracyPositiveColor="#00cc00", lastAccuracyNegativeColor="#cc0000",
    fadeAnimationMaxTime=2, accuracyAnimationMaxTime=5, hintAnimationMaxTime=1
    ) {
    
        this.key = key;
        
        this.accuracyHistory = [];
        this.lastAccuracy = 0;
        this.meanAccuracy = 0;

        this.x = x;
        this.y = y;
        this.radius = radius;
        this.width = width;

        this.totalAlpha = 0;
        this.initialAnimation = true;
        this.endAnimation = false;
        this.isReady = false;
        this.isEnded = false;
        this.fadeAnimationTime = 0;
        this.fadeAnimationMaxTime = fadeAnimationMaxTime;

        this.ringColor = ringColor;
        this.circleColor = circleColor;
        this.checkLineColor = checkLineColor;
        
        this.startAngle = normalizeAngle(-startAngle);
        this.angle = this.startAngle;
        this.angularSpeed = angularSpeed;

        this.checkLineOffset = checkLineOffset;
        this.checkLineWidth = checkLineWidth;

        this.circleShadowBlur = circleShadowBlur;
        this.circleShadowRadius = circleShadowRadius;
        this.circleWidthOffset = circleWidthOffset;

        this.fontColor = fontColor;
        this.fontSize = fontSize;

        this.lastAccuracyNegativeColor = lastAccuracyNegativeColor;
        this.lastAccuracyPositiveColor = lastAccuracyPositiveColor;

        this.animateAccuracy = false;
        this.accuracyAnimationTime = 0;
        this.accuracyAnimationMaxTime = accuracyAnimationMaxTime;

        this.animationHintKeyDown = false;
        this.hintFadeIn = true;
        this.hintFadeOut = false;
        this.hintAnimationTime = 0;
        this.hintAnimationMaxTime = hintAnimationMaxTime;

        window.addEventListener('keypress', (event) => {
            if (event.defaultPrevented) return;
            if (event.key == this.key) {
                this.calculateAccuracy();
            }
        });

        window.addEventListener('keydown', (event) => {
            if (event.defaultPrevented) return;
            if (event.key == HINT_KEY) {
                this.onHintKeyDown();
            }
        });

        window.addEventListener('keyup', (event) => {
            if (event.defaultPrevented) return;
            if (event.key == HINT_KEY) {
                this.onHintKeyUp();
            }
        });
    }

    draw() {
        // ring
        context.lineWidth = this.width;
        context.strokeStyle = getRGBAString(this.ringColor, this.totalAlpha);
        context.beginPath();
        context.arc(this.x, this.y, this.radius, 0, TWOPI, false);
        context.stroke();
        context.closePath();

        // mean accuracy text
        context.fillStyle = getRGBAString(this.fontColor, this.totalAlpha);
        context.font = `${this.fontSize}em ${FONT_FAMILY}`;
        context.textAlign = 'center';
        context.textBaseline = 'middle';
        context.fillText(`${(this.meanAccuracy * 100).toFixed(2)}%`, this.x, this.y + this.radius + this.width * 2.5);
        
        
        var fontColorRgb = hexToRgb(this.fontColor);
        
        // hint text
        if (this.hintFadeIn || this.hintFadeOut) {
            var animationTime = Math.min(this.hintAnimationTime, this.hintAnimationMaxTime) / this.hintAnimationMaxTime;
            var hintAlpha = (this.hintFadeIn) ? lerp(0, 1, animationTime) : lerp(1, 0, animationTime);
            context.fillStyle = `rgba(${fontColorRgb.r}, ${fontColorRgb.g}, ${fontColorRgb.b}, ${hintAlpha})`;
            context.font = `${this.fontSize}em ${FONT_FAMILY}`;
            context.textAlign = 'center';
            context.textBaseline = 'middle';
            context.fillText(`${this.key}`, this.x, this.y - this.radius - this.width * 2);
        }

        if (this.animateAccuracy) {
            // last accuracy
            var partTime = this.accuracyAnimationMaxTime / 10;
            var alpha = (this.accuracyAnimationTime < partTime ) ? lerp(0, 1, this.accuracyAnimationTime/partTime) : lerp(1, 0, (this.accuracyAnimationTime - partTime)/partTime);
            
            context.fillStyle = `rgba(${fontColorRgb.r}, ${fontColorRgb.g}, ${fontColorRgb.b}, ${alpha})`;
            context.font = `${this.fontSize}em ${FONT_FAMILY}`;
            context.textAlign = 'center';
            context.textBaseline = 'middle';
            context.fillText(`${(this.lastAccuracy * 100).toFixed(2)}%`, this.x, this.y);

            // half circle
            context.lineWidth = this.width;
            context.beginPath();
            var halfCircleColor = (this.lastAccuracy < 0) ? this.lastAccuracyNegativeColor : this.lastAccuracyPositiveColor;
            halfCircleColor = hexToRgb(halfCircleColor);
            context.strokeStyle = `rgba(${halfCircleColor.r}, ${halfCircleColor.g}, ${halfCircleColor.b}, ${alpha})`;
            context.arc(this.x, this.y, this.radius, this.startAngle, this.startAngle - PI, this.lastAccuracy > 0);
            context.stroke();
            context.closePath();
        }

        // check line
        const outerRadius = this.radius + this.width/2 + this.checkLineOffset;
        const innerRadius = this.radius - this.width/2 - this.checkLineOffset;
        const cosStartAngle = Math.cos(this.startAngle);
        const sinStartAngle = Math.sin(this.startAngle);
        context.strokeStyle = getRGBAString(this.checkLineColor, this.totalAlpha);
        context.lineWidth = this.checkLineWidth;
        context.beginPath();
        context.moveTo(outerRadius * cosStartAngle + this.x, outerRadius * sinStartAngle + this.y);
        context.lineTo(innerRadius * cosStartAngle + this.x, innerRadius * sinStartAngle + this.y);
        context.stroke();
        context.closePath();

        // moving circle
        context.fillStyle = getRGBAString(this.circleColor, this.totalAlpha);
        context.shadowColor = getRGBAString('#333333', this.totalAlpha);
        context.shadowBlur = this.circleShadowBlur;
        context.shadowOffsetX = this.circleShadowRadius*Math.cos(-this.angle);
        context.shadowOffsetY = this.circleShadowRadius*Math.sin(-this.angle);
        context.beginPath();
        context.arc(this.radius*Math.cos(this.angle) + this.x, this.radius*Math.sin(this.angle) + this.y, 
                    this.width/2 + this.circleWidthOffset, 0, TWOPI, false);
        context.fill();
        context.closePath();
        context.shadowBlur = 0;
        context.shadowOffsetX = 0;
        context.shadowOffsetY = 0;
    }

    getMeanAccuracy() {
        var length = this.accuracyHistory.length;
        if (length == 0) return 0;
        var pluses = this.accuracyHistory.filter(accuracy => accuracy >= 0).length;
        var minuses = length - pluses;
        var sign = pluses > minuses ? 1 : -1;
        return sign * this.accuracyHistory.reduce((sum, value) => sum += Math.abs(value), 0) / length;
    }

    update() {
        var dt = DT * 1e-3;
        
        this.angle += this.angularSpeed * dt;

        if (this.animateAccuracy) {
            this.accuracyAnimationTime += dt;
            if (this.accuracyAnimationTime >= this.accuracyAnimationMaxTime) {
                this.animateAccuracy = false;
            }
        }

        if (this.hintFadeIn || this.hintFadeOut) {
            this.hintAnimationTime += dt;
            if (this.hintAnimationTime >= this.hintAnimationMaxTime && !this.animationHintKeyDown) {
                if (this.hintFadeIn) {
                    this.hintFadeIn = false;
                    this.hintFadeOut = true;
                    this.hintAnimationTime = 0;
                } else {
                    this.hintFadeIn = false;
                    this.hintFadeOut = false;
                }
            }
        }
    }

    startUpdate() {
        if (this.initialAnimation) {
            this.fadeAnimationTime += DT * 1e-3;
            this.totalAlpha = lerp(0, 1, this.fadeAnimationTime / this.fadeAnimationMaxTime);
            if (this.fadeAnimationTime > this.fadeAnimationMaxTime) {
                this.initialAnimation = false;
                this.isReady = true;
                this.fadeAnimationTime = 0;
            }
        }
    }

    stopUpdate() {
        if (this.endAnimation) {
            this.fadeAnimationTime += DT * 1e-3;
            this.totalAlpha = lerp(1, 0, this.fadeAnimationTime / this.fadeAnimationMaxTime);
            if (this.fadeAnimationTime > this.fadeAnimationMaxTime) {
                this.endAnimation = false;
                this.isEnded = true;
                this.fadeAnimationTime = 0;
            }
        }
    }

    calculateAccuracy() {
        if (this.isReady) {
            var normalizedAngle = normalizeAngle(this.angle - this.angularSpeed * DT * 1e-3);
            var angleDifferance = normalizeAngle(this.startAngle - normalizedAngle);
            if (angleDifferance >= PI) {
                angleDifferance = -toRange(angleDifferance, TWOPI, PI, 0, PI);
                var accuracy = toRange(angleDifferance / PI, 0, -1, -1, 0);
            } else {
                var accuracy = 1 - angleDifferance / PI
            }
            this.accuracyHistory.push(accuracy);
            this.lastAccuracy = accuracy;
            this.meanAccuracy = this.getMeanAccuracy();
            this.startAccuracyAnimation();
        }
    }

    startAccuracyAnimation() {
        this.accuracyAnimationTime = 0;
        this.animateAccuracy = true;
    }

    onHintKeyDown() {
        if (this.isReady && !this.animationHintKeyDown) {
            this.animationHintKeyDown = true;
            if (!this.hintFadeIn) this.hintAnimationTime = 0;
            this.hintFadeIn = true;
        }
    }

    onHintKeyUp() {
        if (this.isReady)
            this.animationHintKeyDown = false;
    }
}

function update(context, monorings, gameState) {
    context.fillStyle = BACKGROUND_COLOR;
    context.beginPath();
    context.fillRect(0, 0, canvas.width, canvas.height);
    context.closePath();

    if (!gameState.gameStarted) {
        context.fillStyle = `#333`;
        context.font = `4em ${FONT_FAMILY}`;
        context.textAlign = 'center';
        context.textBaseline = 'middle';
        context.fillText("Нажмите 's' для начала игры", CENTER_X, CENTER_Y/2);
        context.fillText("В момент пересечения черты кружком нажимайте на соответствующую клавишу", CENTER_X, 4*CENTER_Y/6);
        context.fillText(`Нажимайте '${monorings.left.key}' для кружка слева, '${monorings.middle.key}' для кружка по центру и '${monorings.right.key}' для кружка справа`, CENTER_X, 5*CENTER_Y/6);
    } else {
        if (gameState.gameEnded) {
            gameState.allEnded = gameState.allEnded || monorings.array.every((monoring) => monoring.isEnded);
            if (!gameState.allEnded) {
                monorings.array.forEach((monoring) => {
                    monoring.draw();
                    monoring.stopUpdate();
                });
            } else {
                context.fillStyle = `#333`;
                context.font = `5em ${FONT_FAMILY}`;
                context.textAlign = 'center';
                context.textBaseline = 'middle';
                var leftAccuracy = (monorings.left.getMeanAccuracy() * 100).toFixed(2);
                var middleAccuracy = (monorings.middle.getMeanAccuracy() * 100).toFixed(2);
                var rightAccuracy = (monorings.right.getMeanAccuracy() * 100).toFixed(2);
                context.fillText("Точность слева", CENTER_X/2, CENTER_Y/4);
                context.fillText(`${leftAccuracy}%`, CENTER_X/2, CENTER_Y/2);
                context.fillText("Точность по центру", CENTER_X, CENTER_Y/4);
                context.fillText(`${middleAccuracy}%`, CENTER_X, CENTER_Y/2);
                context.fillText("Точность справа", 3*CENTER_X/2, CENTER_Y/4);
                context.fillText(`${rightAccuracy}%`, 3*CENTER_X/2, CENTER_Y/2);
                clearInterval(mainInterval);
            }
        } else {
            gameState.allReady = gameState.allReady || monorings.array.every((monoring) => monoring.isReady);
            monorings.array.forEach((monoring) => {
                monoring.draw();
                if (gameState.allReady) {
                    monoring.update();
                } else {
                    monoring.startUpdate();
                }
            });

            // hint text
            context.fillStyle = `#ccc`;
            context.font = `4em ${FONT_FAMILY}`;
            context.textAlign = 'left';
            context.textBaseline = 'middle';
            context.fillText("Удерживайте 'h' для подсказки", 20, 50);
            context.fillStyle = `#333`;
            context.fillText("Нажмите 's' для остановки игры", 20, 150);
        }
    }
}

// --------------------------------------------------------------

//                                           key  x                   y    radius width   ring clr    circle clr  line clr      start angle       
var leftMonoring    = new Monoring(context, "q", CENTER_X/2,       CENTER_Y,   250, 50,    '#d99694',  '#e46c0a',     '#333333',    getRandomAngle(), getRandomBetween(PI/5, PI/2));
var middleMonoring  = new Monoring(context, "w", CENTER_X,     3*CENTER_Y/4,   500, 75,    '#3a5f8b',  '#e7706d',     '#333333',    getRandomAngle(), getRandomBetween(PI/5, PI/2));
var rightMonoring   = new Monoring(context, "e", CENTER_X*3/2,     CENTER_Y,   250, 50,    '#d99694',  '#e46c0a',     '#333333',    getRandomAngle(), getRandomBetween(PI/5, PI/2));
var monorings = {
    left    : leftMonoring,
    middle  : middleMonoring,
    right   : rightMonoring,
    array   : [leftMonoring, middleMonoring, rightMonoring] 
}
monorings.left.fontSize = monorings.right.fontSize = 5;

var gameState = {
    gameStarted : false,
    gameEnded   : false,
    allReady    : false,
    allEnded    : false
}
console.log(gameState);

window.addEventListener("keypress", (event) => {
    if (event.key == 's') {
        if (gameState.gameStarted && gameState.allReady) {
            gameState.gameEnded = true;
            monorings.array.forEach((monoring) => monoring.endAnimation = true);
        }
        gameState.gameStarted = true;
    }
});

var mainInterval = setInterval(() => update(context, monorings, gameState), DT);
