# Final-Project-si507

## Project Scope

## Data Schema

![Database schema](doc/img/db-schema.png)

Or [access online](https://app.quickdatabasediagrams.com/#/d/oo35Ob).

Explanations on some fields:

- CompanyRating
    - `sample_n`: the amount of rating data. The `value` is the average rating, and `sample_n` indicates the amount of ratings. This is an important factor when evaluating ratings. If n is too small, the rating means little and you probably should not take it seriously.
    - `value`: the rating value scrapped from the web page. This is usually the average of all ratings, assumed that the website did not use other way to compute the overall company rating.
    - `source`: where the rating data comes from, i.e., glassdoor, indeed, or other rating website.
- Company
    - `size`: the size of the company. This can be an important factor for jon seeker as well. It also affects the company culture more or less.
- Link
    - Link will just serve for OneToOne relationship so that other table can avoid having too much flatten fields.
- Address
    - Similar to Link, serve as OneToOne field for other tables about address information.

## Reference & Resources

- [Proposal Link](https://paper.dropbox.com/doc/SI507-Final-Project-by-Shaung-Cheng--Aa3swZraJVTqmfX6hACLwYLsAQ-W3RLpuHtj7eeItw4Hw4SI).

- [Database schema design tool.](https://app.quickdatabasediagrams.com/#/d/oo35Ob)

- [Repository URL](https://github.com/rivernews/Final-Project-si507)