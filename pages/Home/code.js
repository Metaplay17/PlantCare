// async function GetPlants() {
//     let response = await fetch("http://127.0.0.1:5000/plants");
//     let plants = await response.json();
//     return plants;
// }

document.addEventListener("DOMContentLoaded", async () => {
  // Получаем элементы модального окна
  const modalAdd = document.getElementById('modal');
  const openModalAddBtn = document.getElementById("add-btn");
  const closeModalAddBtn = document.getElementById('closeModalBtn');
  const plantForm = document.getElementById('plantForm');

  // Открываем модальное окно
  openModalAddBtn.addEventListener('click', () => {
    modalAdd.style.display = 'block';
    // Устанавливаем текущую дату в поле "Added Date"
    const addedDateInput = document.getElementById('addedDate');
    const today = new Date().toISOString().split('T')[0];
    addedDateInput.value = today;
  });

  // Закрываем модальное окно
  closeModalAddBtn.addEventListener('click', () => {
    modalAdd.style.display = 'none';
  });

  // Закрываем модальное окно при клике вне его области
  window.addEventListener('click', (event) => {
    if (event.target === modalAdd) {
      document.getElementById("adding-info").innerHTML = "";
      modalAdd.style.display = 'none';
    }
  });

  // Обработка отправки формы
  plantForm.addEventListener('submit', async (event) => {
    event.preventDefault(); // Предотвращаем отправку формы
    const formData = new FormData(plantForm);

    data = {
      name: formData.get('name'),
      science_name: formData.get('scienceName'),
      added_date: formData.get('addedDate'),
      place: formData.get('place'),
    };

    if (!CheckSQLInput(data["name"]) || !CheckSQLInput(data["science_name"])) {
      document.getElementById("adding-info").innerHTML = "Use another name";
      return;
    }
    let status = await AddPlant(data);
    if (status === 201) 
    {
      // Закрываем модальное окно после отправки
      modal.style.display = 'none';

      // Очищаем форму
      plantForm.reset();

      document.getElementById("adding-info").innerHTML = "";
      return;
    }
    else if (status >= 500 && status < 600)
    {
      document.getElementById("adding-info").innerHTML = "Internal server error, check internet";
      return;
    }
    else if (status === 409)
      {
        document.getElementById("adding-info").innerHTML = "This name or place is already used";
        return;
      }


  });

});

async function AddPlant(data) {

  let response = await fetch("http://127.0.0.1:5000/plants", {
    method: 'POST',
    body: JSON.stringify(data),
    headers: {
        'Content-Type': 'application/json; charset=UTF-8'
    }
  });
  return response.status;
}

function CheckSQLInput(input) {
  // Примеры ключевых слов и символов, характерных для SQL-инъекций
  const sqlInjectionPattern = /(\b(ALTER|CREATE|DELETE|DROP|EXEC(UTE)?|INSERT( +INTO)?|MERGE|SELECT|UPDATE|UNION( +ALL)?|TRUNCATE|RENAME|REPLACE|LOAD_FILE|OUTFILE|DUMPFILE|BULK +INSERT|GRANT|REVOKE|DENY|DECLARE|FETCH|OPEN|CLOSE|XP_CMDSHELL|SP_OACREATE|WAITFOR +DELAY|BEGIN|END|IF|ELSE|WHILE|CURSOR|PROCEDURE|FUNCTION|TRIGGER|SCHEMA|TABLE|VIEW|INDEX|SEQUENCE|USER|DATABASE|SESSION|TRANSACTION|COMMIT|ROLLBACK|SAVEPOINT|LOCK|UNLOCK|VACUUM|ANALYZE|EXPLAIN|DESCRIBE|SHOW|USE|FROM|WHERE|HAVING|GROUP +BY|ORDER +BY|LIMIT|OFFSET|JOIN|INNER|OUTER|LEFT|RIGHT|FULL|CROSS|NATURAL|USING|ON|AS|CASE|WHEN|THEN|ELSE|END|BETWEEN|LIKE|ILIKE|REGEXP|IN|EXISTS|NOT|NULL|IS|DISTINCT|ANY|ALL|SOME|COLLATE|CAST|CONVERT|NULLIF|COALESCE|IFNULL|NVL)\b|;|--|\/\*|\*\/|@@|@|\$\$|\/\*!.+\*\/|0x[0-9a-fA-F]+|\b(TRUE|FALSE|NULL)\b|\b(AND|OR|XOR|DIV|MOD|BETWEEN|RLIKE|SOUNDS +LIKE|REGEXP +BINARY)\b|\b(CHAR|CONCAT|SUBSTRING|SUBSTR|LENGTH|REPLACE|REVERSE|UPPER|LOWER|TRIM|LTRIM|RTRIM|POSITION|INSTR|LOCATE|LPAD|RPAD|SPACE|REPEAT|HEX|UNHEX|BIN|OCT|ASCII|ORD|CONV|FORMAT|ROUND|CEIL|FLOOR|TRUNCATE|ABS|SIGN|SQRT|POW|POWER|EXP|LOG|LOG10|LN|SIN|COS|TAN|ASIN|ACOS|ATAN|ATAN2|RADIANS|DEGREES|PI|RAND|UUID|MD5|SHA1|SHA2|AES_ENCRYPT|AES_DECRYPT|ENCODE|DECODE|COMPRESS|UNCOMPRESS|CRC32|ENCRYPT|DECRYPT|PASSWORD|OLD_PASSWORD|RANDOM_BYTES|TO_BASE64|FROM_BASE64)\s*\(|\/\*![0-9]{5}|\b(ADDDATE|ADDTIME|CONVERT_TZ|CURDATE|CURRENT_DATE|CURRENT_TIME|CURRENT_TIMESTAMP|CURTIME|DATE|DATEDIFF|DATE_ADD|DATE_FORMAT|DATE_SUB|DAY|DAYNAME|DAYOFMONTH|DAYOFWEEK|DAYOFYEAR|EXTRACT|FROM_DAYS|FROM_UNIXTIME|GET_FORMAT|HOUR|LAST_DAY|LOCALTIME|LOCALTIMESTAMP|MAKEDATE|MAKETIME|MICROSECOND|MINUTE|MONTH|MONTHNAME|NOW|PERIOD_ADD|PERIOD_DIFF|QUARTER|SECOND|SEC_TO_TIME|STR_TO_DATE|SUBDATE|SUBTIME|SYSDATE|TIME|TIMEDIFF|TIMESTAMP|TIMESTAMPADD|TIMESTAMPDIFF|TIME_FORMAT|TIME_TO_SEC|TO_DAYS|TO_SECONDS|UNIX_TIMESTAMP|UTC_DATE|UTC_TIME|UTC_TIMESTAMP|WEEK|WEEKDAY|WEEKOFYEAR|YEAR|YEARWEEK)\s*\(|\b(IF|ELSE|CASE|WHEN|THEN|END|NULLIF|COALESCE|GREATEST|LEAST|BIN_TO_UUID|UUID_TO_BIN|JSON_ARRAY|JSON_ARRAYAGG|JSON_OBJECT|JSON_OBJECTAGG|JSON_QUOTE|JSON_UNQUOTE|JSON_CONTAINS|JSON_CONTAINS_PATH|JSON_EXTRACT|JSON_KEYS|JSON_OVERLAPS|JSON_SEARCH|JSON_VALUE|JSON_ARRAY_APPEND|JSON_ARRAY_INSERT|JSON_INSERT|JSON_MERGE|JSON_MERGE_PATCH|JSON_MERGE_PRESERVE|JSON_REMOVE|JSON_REPLACE|JSON_SET|JSON_DEPTH|JSON_LENGTH|JSON_TYPE|JSON_VALID|JSON_TABLE|JSON_SCHEMA_VALID|JSON_SCHEMA_VALIDATION_REPORT|JSON_PRETTY|JSON_STORAGE_SIZE|JSON_STORAGE_FREE|JSON_ARRAYAGG|JSON_OBJECTAGG)\s*\(|\b(GEOMETRY|POINT|LINESTRING|POLYGON|MULTIPOINT|MULTILINESTRING|MULTIPOLYGON|GEOMETRYCOLLECTION|ST_ASBINARY|ST_ASTEXT|ST_BUFFER|ST_CENTROID|ST_CONTAINS|ST_CONVEXHULL|ST_CROSSES|ST_DIFFERENCE|ST_DIMENSION|ST_DISJOINT|ST_DISTANCE|ST_ENDPOINT|ST_ENVELOPE|ST_EQUALS|ST_EXTERIORRING|ST_GEOHASH|ST_GEOMETRYTYPE|ST_INTERIORRINGN|ST_INTERSECTION|ST_INTERSECTS|ST_ISCLOSED|ST_ISEMPTY|ST_ISSIMPLE|ST_LENGTH|ST_NUMGEOMETRIES|ST_NUMINTERIORRING|ST_NUMPOINTS|ST_OVERLAPS|ST_POINTN|ST_SIMPLIFY|ST_STARTPOINT|ST_SYMDIFFERENCE|ST_TOUCHES|ST_UNION|ST_WITHIN|ST_X|ST_Y)\s*\()/gi;

  if (sqlInjectionPattern.test(input)) {
      return false;
  }
  return true;
}