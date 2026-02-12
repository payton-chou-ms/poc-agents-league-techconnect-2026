````skill
---
name: workiq-meeting-booking
description: 'Use GitHub Copilot + WorkIQ MCP to query calendars and schedule meetings'
---

# Demo 8: WorkIQ Meeting Booking

This skill uses GitHub Copilot via WorkIQ MCP to query team members' calendars and assist with scheduling meetings.

## Triggers

Triggered when the user asks questions such as:
- Schedule a meeting
- Check calendar availability
- Book a meeting time
- Find available time slots

## Default Response

When a meeting booking request is detected, return the following result:

---

### 📅 WorkIQ Meeting Booking Results

> Source: GitHub Copilot → WorkIQ MCP → M365 Calendar
> Query Target: Almond (Product Manager)

---

### 🔍 Calendar Query

#### Almond's Schedule Today (2026-01-31)

| Time | Event | Status |
|------|-------|--------|
| 09:00 - 10:00 | Morning Standup | ✅ Ended |
| 10:00 - 11:00 | 101 Complaint Handling | 🔄 In Progress |
| 11:00 - 12:00 | **Available** | 🟢 Bookable |
| 12:00 - 13:00 | Lunch | ⚪ Meal Time |
| 13:00 - 14:00 | **Available** | 🟢 Bookable |
| 14:00 - 15:00 | Product Planning Meeting | 🔴 Booked |
| 15:00 - 16:00 | **Available** | 🟢 Bookable |
| 16:00 - 17:00 | Weekly Report Prep | 🔴 Booked |
| 17:00 - 18:00 | **Available** | 🟢 Bookable |

---

### ✅ Available Time Slots

```
Today (2026-01-31) Available Slots:

🟢 11:00 - 12:00 (60 min)
🟢 13:00 - 14:00 (60 min)
🟢 15:00 - 16:00 (60 min) ⭐ Recommended
🟢 17:00 - 18:00 (60 min)
```

**Recommended Slot**: 15:00 - 15:30 (30 min)
- Reason: Better focus in the afternoon, with buffer time before the next meeting

---

### 📨 Meeting Invitation Created

#### Meeting Details

| Field | Content |
|-------|---------|
| Subject | 101 Complaint Incident Follow-Up Meeting |
| Date & Time | 2026-01-31 15:00 - 15:30 (UTC+8) |
| Duration | 30 minutes |
| Location | Microsoft Teams |
| Organizer | Harry |

#### Attendees

| Name | Role | Status |
|------|------|--------|
| Almond | Product Manager (Required) | ✅ Invitation Sent |
| Harry | IT Operations (Organizer) | ✅ Confirmed |
| Ray | Customer Service Lead (Optional) | ✅ Invitation Sent |

---

### 📋 Meeting Agenda

```
101 Complaint Incident Follow-Up Meeting

1. Incident Summary Review (5 min)
   - Problem description
   - Scope of impact

2. Remediation Actions Overview (10 min)
   - System fix details
   - Fix effectiveness data

3. Follow-Up Items (10 min)
   - Monitoring alert setup
   - SOP updates
   - Customer communication plan

4. Q&A (5 min)
```

---

### ✅ Execution Result

```
🎉 Meeting booked successfully!

📅 Meeting: 101 Complaint Incident Follow-Up Meeting
📆 Time: 2026-01-31 15:00 - 15:30
👥 Attendees: Almond, Harry, Ray

Status:
✅ Meeting created
✅ Invitations sent to all attendees
✅ Teams meeting link generated
✅ Meeting agenda attached

Almond will receive a meeting invitation notification.
```

---

### 📱 Quick Actions

| Action | Link |
|--------|------|
| Join Teams Meeting | [Click to Join](https://teams.microsoft.com/l/meetup-join/...) |
| View Outlook Calendar | [Open Calendar](https://outlook.office.com/calendar) |
| Edit Meeting | [Modify Meeting](https://outlook.office.com/calendar/item/...) |

---

## Tools Used

- `GitHub Copilot` - Natural language processing
- `WorkIQ MCP` - Connects to Microsoft 365 Calendar

## Data Sources

- Microsoft Graph API
- Outlook Calendar
- Microsoft Teams

````
