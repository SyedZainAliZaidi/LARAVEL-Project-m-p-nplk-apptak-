# M&P Studio AI

This repository holds a small working demo I built during my internship at Muller and Phipps Company Private Limited. It is not a finished product. It is a proof of concept, built to show that an idea I proposed can actually work in practice, not just on paper.

## The idea behind it

While going through the internship, I noticed that Muller and Phipps runs a lot of separate applications for a lot of separate tasks. AppTak, DawaAppTak, DCRS, Salezman and M&P Survey all exist as their own islands, and none of them really talk to each other. If someone wants to know the status of an order, or what a field rep did last week, or how many support tickets are open, they have to go open a different app for each of those questions.

The idea I pitched was simple. Build one internal AI assistant that can sit above all of these systems and answer questions from any department, using the real data each system already holds. The team liked the concept, so I was asked to build a working demo of it before anything real gets planned around it.

## What this repository actually is

This is that demo. It proves the core mechanic works: a single chat interface that can understand what department a question belongs to, pull the right information, and answer in plain language.

Since I do not have access to M&P's real systems at this stage, everything here runs on realistic dummy data instead. The orders, shipments, support tickets, field visits and sales figures are all fake, but they are shaped exactly like the real thing would be, modeled closely after AppTak, DCRS and Salezman style records.

## How it is built

Everything in this demo runs for free, on a local machine, with no paid service involved anywhere.

* FastAPI handles the backend logic and decides what to do with each question
* SQLite stores the dummy department data, no server or installation needed
* Ollama runs a small AI model directly on the machine, so there is no API cost per question
* Chart.js draws the live dashboard graphs straight from the same data
* A plain HTML and JavaScript frontend ties the dashboard and chat together

## How it decides what to do

This is really the heart of the whole idea, and the part worth understanding before anything else. When a question comes in, the system does not just throw it at the AI model blindly. It first checks what kind of question it actually is.

If the question is about something concrete, like an order number, a shipment, sales figures or a support ticket, it goes straight to the database and pulls the exact matching record. If the question is more general, like asking about a policy or how something works, it searches a small knowledge base of company information instead. Either way, the AI model only steps in at the very end, to turn whatever real data was found into a natural, readable answer, rather than guessing at one from scratch.

```
                     user asks a question
                              |
                              v
                     question classifier
                    /                    \
        looks structured               looks general
       (order, shipment,               (policy, how
        sales, ticket)                  something works)
              |                                |
              v                                v
      query the real database         search the knowledge base
      (SQLite for this demo)          (company documentation)
              |                                |
               \                              /
                \                            /
                 v                          v
                    local AI model (Ollama)
                turns the real result into a
                     plain language answer
                              |
                              v
                    shown back in the chat,
               tagged with where it came from
```

In a real production version, the database side would be Muller and Phipps' actual systems, and the knowledge base would be actual company documentation, but the decision making shown above would work the exact same way.

## Why this matters from a systems engineering angle

This is not just a chatbot experiment. What is really being demonstrated here is a routing layer between multiple data sources and a single point of access, with a clear separation between where data lives, how it gets retrieved, and how it gets presented. That separation, deciding intent, fetching from the correct source, then generating a response, is a systems design problem before it is an AI problem. Getting that structure right, in a way that stays reliable and easy to extend as more departments and data sources get added, is exactly the kind of systems engineering work this internship has been about.

## Running it

Everything needed to run this demo locally is inside the project folder. It requires Python, FastAPI, Ollama with a small local model pulled, and a browser. No cloud account and no payment method is needed anywhere in this setup.
