import turtle
#1.设置画布和画笔
t = turtle.Turtle()
t.speed(3)
t.pensize(5)

#2.画苹果的主体(red)
t.color("red")
t.begin_fill()
t.circle(50,180) #画半圆
t.circle(50,180) # 再画一个小一点的半圆，让形状更自然
t.left(90)
t.forward(10)    #封个口
t.end_fill()

#3.画苹果的梗(brown)
t.penup()
t.goto(0,100)
t.pendown()  #落笔
t.color("brown")
t.width(8)
t.left(270)
t.forward(60)

#4.完成后让窗口保持打开
turtle.done()
