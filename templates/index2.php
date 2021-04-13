
<html>
<title>Home</title>

<form name="form_select" id="form_name" method="POST" action="{{ url_for('show_status')}}">
  <select name="select_pers" id="sel_per" class="required">
    <option value="" disabled selected>Select an Option</option>
    {% for val in mem_val%}
      <option value={{val[0]}} >{{val[1]}} </option>
    {% endfor %}
  </select>
  <input type='submit' value='Submit'>
</form>
<!-- <table border = 1>
  {% for val in us_st%}
    <tr>
      <td> {{val[0]}} </td>
      <td> {{val[1]}} </td>
    </tr>
    {% endfor %}
</table> -->
</html>
