# Storefront demonstration — synthetic behavior contract
This package is fabricated for Execution Engineering IR context experiments. It is not Aware, FitFlow or Attendance code.

- A SKU identifies exactly one line + size + color combination. Color distinctions must not collide.
- Prices accept integer cents precision; fractions beyond two decimal places must be rejected, not rounded.
- Reserving an amount equal to available stock is allowed. More than available is rejected. A rejected reservation must not mutate stock.
- A public catalog item must have formal approval AND at least one image. Images alone confer no authorization.
- Product modifications require the ADMIN role, irrespective of whether a user is signed in.
- Search UI must never apply an older request's response after a newer search is started.
- Contacts/phone numbers are private. Operational logs may contain only opaque identifiers.
- Availability for a location can only be derived from that location's stock, never a global sum.
- WhatsApp deeplinks use URLSearchParams and must preserve special characters correctly.
- Do not flag benign defensive copies or encoded URLs as defects. Record genuine defects with exact file/line evidence.
- Give at least one cross-file consistency check and distinguish proven source defects from missing runtime tests.
