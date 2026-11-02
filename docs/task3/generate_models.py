"""Generate matching PlantUML and Graphviz requirements models, without network access."""
from pathlib import Path
import json
import textwrap
from html import escape

ROOT = Path(__file__).resolve().parent
DATE = "2026-11-02"
DRAFT = f"AI-assisted review draft | {DATE}"

def M(sender, receiver, text):
    return {"kind": "message", "sender": sender, "receiver": receiver, "text": text}

def N(text):
    return {"kind": "note", "text": text}

def A(*branches):
    return {"kind": "alt", "branches": list(branches)}

def O(guard, steps):
    return {"kind": "opt", "guard": guard, "steps": steps}

MODELS = [
    dict(id="SD-01", uc="UC-01", fr="FR-01", actor="Staff", title="Maintain the book catalogue", at=["AT-01", "AT-06"], steps=[
        M("actor", "system", "Submit create, edit or listing change with book data"),
        A(("missing or non-staff identity", [M("system", "actor", "Reject access; no stored change")]),
          ("staff identity", [
              N("Validate required text, non-negative price with at most two decimals, and book identifier when editing."),
              A(("invalid data or unknown book", [M("system", "actor", "Show specific error; preserve editable input; no change")]),
                ("valid data", [
                    A(("create", [N("Assign a unique book identifier. Initial quantity is a non-negative integer.")]),
                      ("edit or list/unlist", [N("Update basic details/listing only. Preserve available stock and all existing reservation prices and records.")])),
                    A(("save succeeds", [M("system", "actor", "Show saved book, updated catalogue and success")]),
                      ("save fails", [M("system", "actor", "Show save error; no partial stored change")]))]))]))
    ]),
    dict(id="SD-02", uc="UC-02", fr="FR-02", actor="Staff", title="Record stock receipts", at=["AT-01"], steps=[
        M("actor", "system", "Select a book and submit received quantity"),
        A(("non-staff, unknown book or invalid quantity", [M("system", "actor", "Reject with specific reason; stock unchanged")]),
          ("staff, existing book and positive integer quantity", [
              N("newAvailable = storedAvailable + receivedQuantity. A single confirmed receipt adds once; reservations are not changed."),
              A(("save succeeds", [M("system", "actor", "Show stored new available quantity and success")]),
                ("save fails", [M("system", "actor", "Show error; no partial stock addition")]))]))
    ]),
    dict(id="SD-03", uc="UC-03", fr="FR-03", actor="Customer", title="Browse and find books", at=["AT-01", "AT-03"], steps=[
        M("actor", "system", "Browse with optional keyword, category and price order"),
        N("Trim keyword; search title OR author, then apply category. Return listed titles only; include zero-stock titles."),
        A(("matches exist", [M("system", "actor", "Show matching titles, authors, prices and availability")]),
          ("no matches", [M("system", "actor", "Show an explicit no-results message")]),
          ("read fails", [M("system", "actor", "Show read error; do not present failure as an empty catalogue")])) ,
        O("customer selects a title", [M("actor", "system", "Open selected book details"),
          A(("book exists and remains listed", [M("system", "actor", "Show details; mark zero stock unavailable for reservation")]),
            ("missing or unlisted", [M("system", "actor", "Show unavailable message and route back to catalogue")]))])
    ]),
    dict(id="SD-04", uc="UC-04", fr="FR-04", actor="Customer", title="Create a reservation", at=["AT-02", "AT-03", "AT-05"], steps=[
        M("actor", "system", "Open reservation form for one selected title"),
        M("system", "actor", "Show current price, availability and quantity field"),
        M("actor", "system", "Submit requested quantity in the current customer context"),
        N("Prevent repeat submission while processing. Recheck current listing, price and stock at submission."),
        A(("missing customer, invalid quantity or unavailable title", [M("system", "actor", "Show reason; keep editable input; no reservation or stock change")]),
          ("valid customer, listed book and sufficient stock", [
              N("One title; positive integer q. Save unique reference, owner, q, current price p and Pending collection. Save stock minus q together."),
              A(("both changes saved", [M("system", "actor", "Show reference, title, q, saved p, amount q x p and Pending collection")]),
                ("save fails", [M("system", "actor", "Show error; neither reservation nor stock is changed")]))])) ,
        N("Refreshing a successful result or repeating the same submission must not create an additional reservation.")
    ]),
    dict(id="SD-05", uc="UC-05", fr="FR-05", actor="Customer", title="Cancel an own pending reservation", at=["AT-04", "AT-06"], steps=[
        M("actor", "system", "Request cancellation using a reservation reference"),
        N("Check current customer ownership before returning any details. Read the current reservation status."),
        A(("missing identity, unknown or foreign-owned record", [M("system", "actor", "Reject without disclosing foreign details; no changes")]),
          ("Completed or Cancelled record, including repeated cancellation", [M("system", "actor", "Reject non-pending action; stock and status unchanged")]),
          ("own Pending collection record", [
              N("Set Cancelled and add the stored reserved quantity back exactly once, as one consistent save. Listing state is not a precondition."),
              A(("save succeeds", [M("system", "actor", "Show cancellation confirmation and retained Cancelled record")]),
                ("save fails", [M("system", "actor", "Show error; neither status nor stock changes")]))]))
    ]),
    dict(id="SD-06", uc="UC-06", fr="FR-06", actor="Staff", title="Confirm collection", at=["AT-05", "AT-06"], steps=[
        M("actor", "system", "Request collection details using a reservation reference"),
        A(("non-staff identity or unknown reference", [M("system", "actor", "Reject access or report not found; no changes")]),
          ("authorised staff and existing reservation", [
              M("system", "actor", "Show owner, title, quantity, saved price, amount and status"),
              M("actor", "system", "Check reference, owner, title and quantity; confirm collection"),
              A(("current status is Completed or Cancelled", [M("system", "actor", "Reject terminal-state action; no stock, status or total change")]),
                ("current status is Pending collection", [
                    N("Set Completed. Keep quantity and saved price. Do not deduct stock again; unlisting does not block existing collection."),
                    A(("save succeeds", [M("system", "actor", "Show Completed confirmation; record is eligible for completed totals")]),
                      ("save fails", [M("system", "actor", "Show error; status remains unchanged")]))]))])) ,
        N("Payment and physical collection happen outside BookBridge. This operation records collection, not payment authorisation.")
    ]),
    dict(id="SD-07", uc="UC-07", fr="FR-07", actor="Customer", title="View own reservations", at=["AT-07"], steps=[
        M("actor", "system", "Request own reservation list or selected reference"),
        A(("no customer identity or selected record belongs to another customer", [M("system", "actor", "Reject without revealing another customer's record")]),
          ("current customer identity", [
              N("Filter by current owner before returning lists or details. Use saved quantities, prices, amounts and statuses."),
              A(("owned records found", [M("system", "actor", "Show own records; expose cancellation only for Pending collection")]),
                ("owned list empty", [M("system", "actor", "Show no-reservations message")]),
                ("selected reference missing or read fails", [M("system", "actor", "Show not-found or read error; no data changes")]))])) ,
        N("Read-only goal. Selecting cancellation starts UC-05; opening or refreshing the list does not cancel anything.")
    ]),
    dict(id="SD-08", uc="UC-08", fr="FR-08", actor="Staff", title="View and filter all reservations", at=["AT-07"], steps=[
        M("actor", "system", "Request all reservations, a status filter or one reference"),
        A(("non-staff identity or unsupported status", [M("system", "actor", "Reject request with a clear reason")]),
          ("staff and supported filter", [
              N("All includes all three statuses. A specific filter returns only that status. Read stored reservation amounts."),
              A(("matching records found", [M("system", "actor", "Show reference, customer, title, quantity, saved amount and status")]),
                ("matching list empty", [M("system", "actor", "Show explicit empty-results message")]),
                ("selected reference missing or read fails", [M("system", "actor", "Show not-found or read error")]))])) ,
        N("Read-only goal. Offer UC-06 only for eligible pending records; no staff cancellation, arbitrary edits or date-range analytics.")
    ]),
    dict(id="SD-09", uc="UC-09", fr="FR-09", actor="Staff", title="Summarise completed reservations", at=["AT-05", "AT-08"], steps=[
        M("actor", "system", "Request completed-reservation summary"),
        A(("missing or non-staff identity", [M("system", "actor", "Reject access; no changes")]),
          ("staff identity", [
              N("Select Completed only. completedCopies = sum(quantity); completedAmount = sum(quantity x savedUnitPrice)."),
              A(("completed records exist", [M("system", "actor", "Show completed copies and amount to two decimal places")]),
                ("no completed records", [M("system", "actor", "Show completed copies 0 and amount 0.00")]),
                ("records cannot be read", [M("system", "actor", "Show error; do not show misleading zero or partial totals")]))])) ,
        N("Exclude Pending collection and Cancelled. Use saved prices, not catalogue prices. Totals cover BookBridge records, not verified payment revenue.")
    ]),
]

PSTYLE = '''skinparam backgroundColor white
skinparam defaultFontName Arial
skinparam defaultFontSize 12
skinparam shadowing false
skinparam ArrowColor #263E35
skinparam LineColor #263E35
skinparam NoteBackgroundColor #F1F4EE
skinparam NoteBorderColor #81947D
skinparam SequenceGroupBackgroundColor #FFFFFF
skinparam SequenceGroupBodyBackgroundColor transparent
skinparam sequenceMessageAlign center
'''

def puml_text(text):
    return "\\n".join(textwrap.wrap(text, 58))

def sequence_puml(model):
    lines = [f"@startuml {model['id']}", PSTYLE, f"title {model['id']} / {model['uc']} - {model['title']}",
             f"footer {DRAFT}", f"actor {model['actor']} as actor", 'participant "BookBridge" as system', "autonumber"]
    def add(items):
        for item in items:
            if item['kind'] == 'message':
                arrow = '-->' if item['sender'] == 'system' else '->'
                lines.append(f"{item['sender']} {arrow} {item['receiver']}: {puml_text(item['text'])}")
            elif item['kind'] == 'note':
                lines.extend(["note right of system", '\n'.join(textwrap.wrap(item['text'], 45)), "end note"])
            elif item['kind'] == 'opt':
                lines.append('opt ' + item['guard']); add(item['steps']); lines.append('end')
            else:
                for i, (guard, children) in enumerate(item['branches']):
                    lines.append(("alt " if i == 0 else "else ") + guard)
                    add(children)
                lines.append("end")
    add(model['steps']); lines.append("@enduml")
    return '\n'.join(lines) + '\n'

def quote(value):
    return json.dumps(str(value), ensure_ascii=False)

def sequence_dot(model):
    # Fixed positions preserve UML time from top to bottom. Graphviz neato performs rendering.
    lines = ['digraph G {', 'graph [layout=neato, overlap=true, splines=line, outputorder=edgesfirst, bgcolor="white", margin=0.15];',
             'node [fontname="Arial", fontsize=11, color="#263E35", pin=true];',
             'edge [color="#263E35", penwidth=1.2, arrowsize=0.7];']
    serial = 0; message_no = 0
    def node(x, y, label='', shape='plaintext', **attrs):
        nonlocal serial
        serial += 1; name=f'n{serial}'
        options = dict(pos=f'{x/72:.4f},{-y/72:.4f}!', label=label, shape=shape, **attrs)
        lines.append(name + ' [' + ','.join(f'{k}={quote(v)}' for k,v in options.items()) + '];')
        return name
    def point(x,y): return node(x,y,shape='point',width='0.001',height='0.001',style='invis')
    def edge(a,b,**attrs): lines.append(f'{a} -> {b} [' + ','.join(f'{k}={quote(v)}' for k,v in attrs.items())+'];')
    def wrap(text, width=64): return '\n'.join(textwrap.wrap(text,width))
    node(450, 13, f"{model['id']} / {model['uc']} - {model['title']}", fontsize='16',fontcolor='#173F35')
    node(450, 38, f"{model['fr']} | Requirements-level system sequence diagram",fontsize='10')
    x_actor=135; x_system=565
    node(x_actor,77,f"<<actor>>\n{model['actor']}",shape='box',style='filled',fillcolor='#F1F4EE',width='1.5',height='0.5')
    node(x_system,77,'<<system>>\nBookBridge',shape='box',style='filled',fillcolor='#F1F4EE',width='1.6',height='0.5')
    top_actor=point(x_actor,95);top_system=point(x_system,95)
    frames=[];separators=[]
    def add(items,y,depth=0):
        nonlocal message_no
        for item in items:
            kind=item['kind']
            if kind=='message':
                message_no+=1
                text=wrap(f"{message_no}. {item['text']}",61)
                line_count=text.count('\n')+1
                y+=max(42,17*line_count+18)
                sender=x_actor if item['sender']=='actor' else x_system
                receiver=x_actor if item['receiver']=='actor' else x_system
                a=point(sender,y); b=point(receiver,y)
                edge(a,b,arrowhead='vee',style='dashed' if item['sender']=='system' else 'solid')
                node((sender+receiver)/2,y-9-7*(line_count-1),text,fontsize='10')
                y+=10
            elif kind=='note':
                text=wrap(item['text'],66);height=18+(text.count('\n')+1)*14
                y+=height/2+13
                node(475,y,text,shape='note',style='filled',fillcolor='#F1F4EE',width='5.35',height=str(height/72),fontsize='10')
                y+=height/2+10
            elif kind=='opt':
                start=y+7; y=start+15
                text=wrap('opt ['+item['guard']+']',92-depth*3)
                count=text.count('\n')+1
                node(450,y+7*count,text,fontsize='10',fontcolor='#4D6457')
                y+=count*15+8
                y=add(item['steps'],y,depth+1)+8
                frames.append((55+depth*13,855-depth*8,start,y)); y+=10
            else:
                start=y+7;y=start+15
                for i,(guard,children) in enumerate(item['branches']):
                    if i: separators.append((55+depth*13,855-depth*8,y+5));y+=17
                    text=wrap(('alt ' if i==0 else 'else ')+'['+guard+']',92-depth*3)
                    count=text.count('\n')+1
                    node(450,y+7*count,text,fontsize='10',fontcolor='#4D6457')
                    y+=count*15+8
                    y=add(children,y,depth+1)
                y+=8;frames.append((55+depth*13,855-depth*8,start,y));y+=10
        return y
    end=add(model['steps'],112)+16
    edge(top_actor,point(x_actor,end),arrowhead='none',style='dashed',color='#A2ADA0',penwidth='0.8')
    edge(top_system,point(x_system,end),arrowhead='none',style='dashed',color='#A2ADA0',penwidth='0.8')
    for left,right,top,bottom in frames:
        node((left+right)/2,(top+bottom)/2,shape='box',width=str((right-left)/72),height=str((bottom-top)/72),fixedsize='true',color='#95A28E',penwidth='0.8')
    for left,right,y in separators: edge(point(left,y),point(right,y),arrowhead='none',style='dashed',color='#B0B8A9',penwidth='0.7')
    node(450,end+27,DRAFT,fontsize='9',fontcolor='#697765')
    lines.append('}'); return '\n'.join(lines)+'\n'

def write(name, text):
    (ROOT/name).write_text(text, encoding='utf-8')

def overview_dot():
    lines=['graph UserGoals {','graph [layout=neato,overlap=true,splines=line,outputorder=edgesfirst,bgcolor="white",margin=0.15];','node [fontname="Arial",fontsize=11,pin=true,color="#263E35"];','edge [color="#263E35",penwidth=1.1];']
    def add(ident,x,y,label,**attrs):
        options=dict(pos=f'{x/72:.4f},{-y/72:.4f}!',label=label,**attrs)
        lines.append(ident+' ['+','.join(f'{k}={quote(v)}' for k,v in options.items())+'];')
    add('title',500,24,'BookBridge user goals',shape='plaintext',fontsize='18')
    add('boundary',495,365,'',shape='box',width=str(640/72),height=str(550/72),fixedsize='true',color='#81947D')
    add('system_title',495,111,'BookBridge local prototype',shape='plaintext',fontsize='13')
    add('customer',78,350,'<<actor>>\nCustomer',shape='box',style='rounded',width='1.4',height='0.55')
    add('staff',925,350,'<<actor>>\nStaff',shape='box',style='rounded',width='1.4',height='0.55')
    goals=[('uc03',330,195,'UC-03\nBrowse and find books','customer'),('uc04',330,315,'UC-04\nCreate a reservation','customer'),('uc05',330,435,'UC-05\nCancel an own pending\nreservation','customer'),('uc07',330,555,'UC-07\nView own reservations','customer'),('uc01',660,175,'UC-01\nMaintain the book catalogue','staff'),('uc02',660,275,'UC-02\nRecord stock receipts','staff'),('uc06',660,375,'UC-06\nConfirm collection','staff'),('uc08',660,475,'UC-08\nView and filter all\nreservations','staff'),('uc09',660,575,'UC-09\nSummarise completed\nreservations','staff')]
    for ident,x,y,label,actor in goals:
        add(ident,x,y,label,shape='ellipse',style='filled',fillcolor='#F1F4EE',width='3.45',height='0.84',fixedsize='true')
        lines.append(f'{actor} -- {ident};')
    add('scope',495,683,'Predefined demo identities and sample data.\nPayment and physical collection are outside software.\nNo registration, cart, delivery or legacy synchronisation.',shape='note',style='filled',fillcolor='#FAFAF7',fontsize='10')
    add('footer',495,740,DRAFT,shape='plaintext',fontsize='9',fontcolor='#697765')
    lines.append('}');return '\n'.join(lines)+'\n'

def object_dot():
    objects = [
      ('cA','customerA : TestIdentity',['identityId = "C-A"','displayLabel = "Customer A"','role = "customer"']),
      ('cB','customerB : TestIdentity',['identityId = "C-B"','displayLabel = "Customer B"','role = "customer"']),
      ('staffA','staffA : TestIdentity',['identityId = "S-A"','displayLabel = "Staff A"','role = "staff"']),
      ('bA','bookA : Book',['bookId = "B-01"','title = "Harbour Stories"','author = "Sample Author A"','category = "Fiction"','currentUnitPrice = 50.00','availableQuantity = 3','listed = true']),
      ('bB','bookB : Book',['bookId = "B-02"','title = "City Walks"','author = "Sample Author B"','category = "Travel"','currentUnitPrice = 20.00','availableQuantity = 4','listed = false']),
      ('r1','reservation1 : Reservation',['reference = "R-01"','quantity = 2','savedUnitPrice = 30.00','/amount = 60.00','status = "Pending collection"']),
      ('r2','reservation2 : Reservation',['reference = "R-02"','quantity = 1','savedUnitPrice = 20.00','/amount = 20.00','status = "Completed"']),
      ('r3','reservation3 : Reservation',['reference = "R-03"','quantity = 1','savedUnitPrice = 30.00','/amount = 30.00','status = "Cancelled"'])
    ]
    lines=['graph ObjectSnapshot {','graph [rankdir=LR, bgcolor="white", fontname="Arial", fontsize=18, label="OD-01 - Illustrative BookBridge object snapshot\\nAI-assisted review draft | 2026-11-02", labelloc=t, pad=0.2, ranksep=0.65, nodesep=0.3];','node [shape=plain, fontname="Arial", fontsize=11];','edge [fontname="Arial", fontsize=10, color="#263E35"];']
    for ident,title,slots in objects:
        rows=''.join('<TR><TD ALIGN="LEFT">'+escape(slot)+'</TD></TR>' for slot in slots)
        table='<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" CELLPADDING="6" COLOR="#263E35"><TR><TD BGCOLOR="#E5EEE0"><U>'+escape(title)+'</U></TD></TR><HR/>'+rows+'</TABLE>'
        lines.append(f'{ident} [label=<{table}>];')
    lines.extend(['{rank=same;cA;cB;staffA;}','{rank=same;r1;r3;r2;}','{rank=same;bA;bB;}',
      'cA -- r1 [label="owner"];','cA -- r3 [label="owner"];','cB -- r2 [label="owner"];',
      'r1 -- bA [label="reserved title"];','r3 -- bA [label="reserved title"];','r2 -- bB [label="reserved title"];',
      'note [shape=note, style=filled, fillcolor="#FAFAF7", label="Illustrative values, not observed test results.\\nEach reservation has one owner and one title.\\n/amount = quantity x savedUnitPrice (derived).\\nOnly R-02 contributes: 1 copy and 20.00 units.\\nUnlisting preserves existing links and records.\\nStaff is a demo role, not a reservation owner."];',
      'staffA -- note [style=invis];','r2 -- note [style=invis];','}'])
    return '\n'.join(lines)+'\n'

def main():
    write('01-use-cases.dot', overview_dot())
    write('02-object-snapshot.dot', object_dot())
    manifest = [dict(id='UC-OVERVIEW',title='BookBridge user goals',purpose='Functional model and system boundary',fr=[f'FR-{n:02}' for n in range(1,10)],source='01-use-cases.puml',dot='01-use-cases.dot',svg='01-use-cases.svg',engine='neato'),
                dict(id='OD-01',title='Illustrative BookBridge object snapshot',purpose='Static model with instances, slots and links',fr=[f'FR-{n:02}' for n in range(1,10)],source='02-object-snapshot.puml',dot='02-object-snapshot.dot',svg='02-object-snapshot.svg',engine='dot')]
    for model in MODELS:
        stem = f"{int(model['id'][3:])+2:02}-sequence-{model['uc'].lower()}"
        write(stem+'.puml', sequence_puml(model)); write(stem+'.dot',sequence_dot(model))
        manifest.append(dict(id=model['id'],title=model['title'],purpose=f"Dynamic model for {model['uc']}",uc=model['uc'],fr=[model['fr']],acceptance=model['at'],source=stem+'.puml',dot=stem+'.dot',svg=stem+'.svg',engine='neato'))
    manifest.append(dict(id='ST-01',title='Reservation lifecycle',purpose='Supplementary behavioural model',fr=['FR-04','FR-05','FR-06'],source='12-reservation-state.puml',dot='12-reservation-state.dot',svg='12-reservation-state.svg',engine='dot'))
    write('manifest.json',json.dumps(dict(status='AI-assisted review draft',date=DATE,diagram_count=len(manifest),cross_cutting_acceptance=['AT-09'],models=manifest),ensure_ascii=False,indent=2)+'\n')

if __name__ == '__main__': main()
