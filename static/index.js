var max_widget_z = 0

$(document).ready(function() {
    // connect to socket.io server
    var socket = io();

    // Initialize function called from Python
    socket.on('initialize', function(data) {
        //set title
        title = data['NARS_name']
        $('#NARS_title').html(title)

        //create buffer widgets
        buffer_dict = data['buffers']
        var i = 0;
        for (const [key, value] of Object.entries(buffer_dict)) {
            const buffer_name = value['buffer_name']
            let clone = $("#buffer-card").clone();
            clone_DOM = clone[0]
            clone_DOM.hidden = false;
            //make_card_draggable(clone_DOM);
            clone.attr("id",buffer_name.split(' ').join(''));

            clone.css({top: i*100 + "px", left: 0});
            console.log(clone.find("h1").html());
            clone.find("h1").html(buffer_name);
            $("#inputcard").after(clone);
            i += 1;
        }
    })

    // make all widgets draggable
    for(let widget_card of document.querySelectorAll(".widget-card")){
        make_card_draggable(widget_card);
    }

    //https://stackoverflow.com/questions/9334084/moveable-draggable-div
    // parameter: card, HTML dom element of widget card
    function make_card_draggable(card) {
        card.querySelector(".widget-card-titlebar").addEventListener('mousedown', function(e) {
            $(card).css('z-index', max_widget_z++);
            var offsetX = e.clientX - parseInt(window.getComputedStyle(card).left);
            var offsetY = e.clientY - parseInt(window.getComputedStyle(card).top);

            function mouseMoveHandler(e) {
              card.style.top = (e.clientY - offsetY) + 'px';
              card.style.left = (e.clientX - offsetX) + 'px';
            }

            function reset() {
              window.removeEventListener('mousemove', mouseMoveHandler);
              window.removeEventListener('mouseup', reset);
            }

            window.addEventListener('mousemove', mouseMoveHandler);
            window.addEventListener('mouseup', reset);
        });
    }

    // call on add task to buffer
    socket.on('add_task_to_buffer',function (data){
        buffer_id = data["buffer_name"].split(' ').join('');
        new_row_html = "<tr id=\"" + buffer_id + data['sentence_ID'] + "\">"
        new_row_html += "<th>" + data['sentence'].replace('>', '&gt').replace('<', '&lt') + "</th>"
        new_row_html += "<th>" + data['budget'].replace('>', '&gt').replace('<', '&lt') + "</th>"
        new_row_html += "</tr>"
        new_row = $("#" + buffer_id + " tr:last").after(new_row_html);
        new_row.attr('id', );
    });

    // call on add task to buffer
    socket.on('remove_task_from_buffer',function (data){
        buffer_id = data["buffer_name"].split(' ').join('');
        $("#" + buffer_id + data['sentence_ID']).remove();
    });

    /*
        INITIALIZE MEMORY NETWORK GRAPH
        see https://github.com/vasturiano/force-graph
    */
    // Create graph data storage
    init_memory = {
        "nodes" : [
        ],
        "links" : [
        ]
    };

    // Create graph
    const memory_graph = ForceGraph()
    memory_graph($("#memory-graph-container")[0])
        .linkDirectionalArrowLength(4)
        .linkDirectionalArrowRelPos(1)
        .graphData(init_memory)
        .nodeAutoColorBy('group')
        .nodeId("id")
        .nodeCanvasObject((node, ctx, globalScale) => {
          const label = node.id;

          let fontSize = 12/globalScale;
          if(node.group == "statement"){
            // statement
            fontSize = 16/globalScale;
          }
          ctx.font = `${fontSize}px Sans-Serif`;
          const textWidth = ctx.measureText(label).width;
          const bckgDimensions = [textWidth, fontSize].map(n => n + fontSize * 0.2); // some padding

          ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
          ctx.fillRect(node.x - bckgDimensions[0] / 2, node.y - bckgDimensions[1] / 2, ...bckgDimensions);

          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
          ctx.fillStyle = node.color;
          ctx.fillText(label, node.x, node.y);

          node.__bckgDimensions = bckgDimensions; // to re-use in nodePointerAreaPaint
        })
        .nodePointerAreaPaint((node, color, ctx) => {
            ctx.fillStyle = color;
            const bckgDimensions = node.__bckgDimensions;
            bckgDimensions && ctx.fillRect(node.x - bckgDimensions[0] / 2, node.y - bckgDimensions[1] / 2, ...bckgDimensions);
        }).onNodeClick(node => {
            // Center/zoom on node
            console.log("click")
            memory_graph.centerAt(node.x, node.y, 500);
            socket.emit('get_concept_info', node.id);
        });


    //add a new node to the graph
    socket.on('add_node_to_memory_graph',function (data){
        let { nodes, links } = memory_graph.graphData();
        let id = data["concept_ID"];
        let group = data["term_type"];
        if(group == "atomic"){
            color = "green"
        }else if (group == "statement"){
            color = "red"
        }
        memory_graph.graphData({
            nodes: [...nodes, { id: id,
                                group: group,
                                color: color}],
            links: links
        });
    });

    //add a new link to the graph
    socket.on('add_link',function (data){
        let { nodes, links } = memory_graph.graphData();

        let group = data["link_type"];
        // set link color
        if(group == "termlink"){
            color = "lightblue";
        }
        // create new link object
        new_link = {
            source: data["link_source"],
            target: data["link_target"],
            group: group,
            color: color
        }
        //update graph with new link
        memory_graph.graphData({
            nodes: nodes,
            links: [...links, new_link]
        });
    });

    //show concept info
    socket.on('show_concept_info',function (data){
        let { nodes, links } = memory_graph.graphData();
        let id = data["concept_ID"];
        let beliefs = null;
        let beliefs_key = "beliefs"
        if(beliefs_key in data){
            beliefs = data[beliefs_key];
        }


        // create concept card
        let clone = $("#concept-card").clone();
        clone_DOM = clone[0]
        clone_DOM.hidden = false;
        clone.attr("id","conceptInfoBox" + id);
        clone.find("h1").html("concept " + id);
        $("#sidebar-right-titlebar").after(clone);
    });


    $('form#narseseInputForm').submit(function(event) {
        input_string = $("#narseseInputTextbox").val()
        $("#narseseInputTextbox").val("")
        console.log(input_string)
        socket.emit('send_input', input_string);
        return false;
    });

});



