---
title: DC Motor Speed Control System 进展之UART
date: 2026-02-24T10:55:00
categories: 技术探索
tags:
  - 项目
---

这个项目的系列文章是为了记录项目中涉及到的理论、步骤、以及错误。

# 理论

## UART

（universal asynchronous receiver transmitter）UART是一种点对点异步串行通信协议，让发送端和接收端相互通信。

1、uart没有共享时钟，发送端和接收端各自拥有独立的时钟。

2、uart的发送端和接收端只通过两根数据线（RX和TX）通信

![](20260224-120917.png "Universal Asynchronous Receiver Transmitter")
