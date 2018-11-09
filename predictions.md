---
layout: page
title: Predictions
permalink: /predictions/
---

While future efforts will be more heavily and cleanly automated, for the time being this page is manually updated by me. Please be patient.

Also note that the model is nowhere near optimised - it is more than likely that changes to the model will greatly affect the predictions. Take these as a current best guess...

These are my predictions for the coming round of VSBL baseball:

Updated: 8 November

{% for grade in site.data.next_round_predictions.grades %}
<details>
    <summary>{{ grade.name }}</summary>
<table class="table">
  <tr>
    <th>Home Team</th>
    <th>Home Chance</th>
    <th>Away Chance</th>
    <th>Away Team</th>
  </tr>
{% for game in grade.games %}
  <tr>
    <td> {{ game.team_home }} </td>
    <td> {{ game.chance_home }}% </td>
    <td> {{ game.chance_away }}% </td>
    <td> {{ game.team_away }} </td>
  </tr>
{% endfor %}
</table>
</details>
{% endfor %}
