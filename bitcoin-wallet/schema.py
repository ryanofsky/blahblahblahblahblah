"""
python schema.py | dot -Tsvg > schema.svg
"""

from collections import namedtuple

Table = namedtuple("Table", "table desc cols")
Col = namedtuple("Col", "col desc ref")
Ref = namedtuple("Ref", "table col")

tables = [
  Table("keypool", "CKeyPool"
      Col("pool", "CKeyPool")
  ])
  Table("Transactions", [
      Col("txid", "uint256", None),
      Col("tx", "CTransaction", None)
  ]),
  Table("Keys", [
      Col("address", "CTxDestination", None),
      Col("txid", "uint256", Ref("Transactions", "txid"))
  ]),
]

GRAPH = """
digraph g {{ graph [ rankdir = "LR" ];

{tables}
{refs}

}}"""

TABLE = """
  "{table}" [
    shape=none
    label=<
      <table border="0" cellspacing="0" cellborder="1">
        <tr><td bgcolor="lightblue2"><font face="Times-bold" point-size="20">{table}</font></td></tr>
        {cols}
      </table>
    >];
"""

COL = """
  <tr><td bgcolor="grey96" align="left" port="{col}"><font face="Times-bold">{col}</font>  <font color="#535353">{desc}</font></td></tr>
"""

REF = """
  "{table.table}":{col.col} -> "{col.ref.table}":{col.ref.col}
"""

print(GRAPH.format(
    tables="\n".join(TABLE.format(table=table.table, cols="\n".join(COL.format(col=col.col, desc=col.desc)  for col in table.cols)) for table in tables),
    refs="\n".join(REF.format(table=table, col=col) for table in tables for col in table.cols if col.ref is not None)))
