# AI Email Agent

An AI-powered email management agent that automatically monitors Gmail, understands incoming emails using Google Gemini, classifies their importance, applies intelligent labels, identifies important messages, and processes invoice attachments.

## 🚀 Overview

AI Email Agent is designed to automate repetitive email-management tasks.

Instead of manually checking every incoming email, the agent continuously monitors Gmail and uses AI to understand the content of each message.

The agent can:

- Analyze incoming emails using Google Gemini
- Classify emails by category
- Determine email importance and urgency
- Identify whether an action is required
- Automatically apply Gmail labels
- Mark high-importance emails as Important
- Detect email attachments
- Download invoice attachments
- Upload invoices to Google Drive
- Extract invoice information using AI
- Store extracted invoice data in SQLite
- Run continuously in the background
- Provide a simple Windows desktop interface to start and stop the agent

## ✨ Features

### 📧 Intelligent Email Analysis

Each new email is analyzed by Gemini based on:

- Category
- Importance
- Urgency
- Action required
- Summary
- Recommended action

Supported categories include:

- Work
- Finance
- Travel
- Shopping
- Job
- Education
- Social
- Promotion
- Security
- Invoice
- Other

### ⭐ Important Email Detection

The agent identifies emails that require attention, including:

- Urgent requests
- Deadlines
- Meetings
- Interviews
- Exams
- Payment-related emails
- Security alerts
- Job-related actions
- Work tasks

High-importance emails are automatically marked as **Important** in Gmail.

### 🏷️ Automatic Gmail Labels

The agent creates and applies labels such as:

```text
AI/Work
AI/Finance
AI/Travel
AI/Invoice
AI/Job
AI/Security
