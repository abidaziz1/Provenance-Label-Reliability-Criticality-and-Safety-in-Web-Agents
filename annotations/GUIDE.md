# Annotation guide, version 0.1 (draft, 26 Sep 2026)

For annotators. You need no access to the research repo. You receive one HTML file, open it in a browser, answer three questions per item, and send the file it saves to Abid Aziz. An item takes about a minute.

## What you are looking at

Each item comes from an archived web page that a web agent visited during a real task (the Mind2Web dataset). A program marked one region of that page as content the website did not write itself: an ad, a user review, or a listing from a seller. Inside that region is a control an agent could click or type into.

We want to know whether the program was right. Its mistakes decide whether one of our numbers is real.

For each item the page shows:

- the website's name;
- the region: its HTML tag, its class and id strings, how much of the page it covers, and the first 300 characters of its text;
- the control: its tag, its visible text, and its role if it has one;
- the chain of tags from the top of the page down to the region.

You see text and structure, not a screenshot. The archive keeps no screenshots with these pages.

## Rules

1. **Work alone and blind.** Do not discuss items with the other annotator until you have both sent your files. The page does not show you what the program decided, beyond the fact that it flagged the region.
2. **Treat the page text as data.** Some pages contain text that tries to give instructions, such as "ignore previous instructions" or "click here to verify". Never follow it, and never open links you see in it. If an item looks like an attack, answer the questions as usual and add a note.
3. **No lookups.** Judge from what the item shows. Do not visit the live website.
4. **Use "can't tell" when it applies.** A clear "can't tell" is worth more than a guess.
5. **Take breaks.** Stop after 50 items and come back later. The page remembers where you were in the same browser, but download your file at the end of every session in case it does not.

## The three questions

### Q1. Who wrote or supplied the content in this region?

| Answer | Choose it when | Examples |
| --- | --- | --- |
| Third-party ad | A paid placement from another company, or an ad network slot | "Sponsored", Google ad slots, Taboola feeds, "Advertisement" |
| Users | People who use the site wrote it | reviews, comments, questions and answers, forum posts |
| Sellers or partners | Businesses other than the site supplied it, and the site hosts it | marketplace listings, hotel or seller pages, partner offers |
| The site itself | The website's own interface or its own promotions | navigation, search forms, filters, a banner for the site's own sale or credit card, even when labeled "Advertisement" |
| Can't tell | The item does not show enough | |

**Two traps.**

- A class name with "ad" in it does not make a region an ad. A class such as `adv-options` can mean advanced options, and `promo-ad-banner` can be the site's own banner. Random-looking strings can contain "ad" by chance.
- A region that covers most of the page is almost never third-party. A wrapper around the whole search form is the site itself.

### Q2. Is the control part of the site's own interface?

Answer **yes** for the site's navigation, search box, filters, sort menus, account links and the site's own buttons, even when they sit inside the flagged region. Answer **no** when the control belongs to the ad, the review or the listing: "Shop now" on an ad, "Helpful" on a review, "Contact seller" on a listing. Otherwise answer **can't tell**.

### Q3. Before the control, is there a visible cue that the region is third-party or user content?

Look at the region's text and the tag chain. Answer **yes** if a reader would see a cue such as "Sponsored", "Ad", "Advertisement", "Review by", a user name with a date, or "Sold by". Answer **no** if nothing visible marks it. Answer **can't tell** if the item does not show enough.

## Saving and sending

1. Click **Download my labels**. The file is named `labels_<your initials>_<batch>_<date>.json`.
2. Email it to Abid Aziz. Do not edit the file.
3. Abid Aziz commits it to `annotations/raw/` in the research repo.

## Changes to this guide

Any change raises the version number, and the version is written into every label file. Items labeled under different versions are analysed separately.
