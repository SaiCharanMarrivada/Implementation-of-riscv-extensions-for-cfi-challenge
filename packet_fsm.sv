typedef enum logic [1:0] {
    IDLE,
    CHECK,
    ERROR
} State;

module packet_fsm (
    input logic clk,
    input logic reset,
    input logic [31:0] packet,
    output State state
);
    localparam logic [7:0] SET = 8'h01;
    localparam logic [7:0] JUMP = 8'h02;
    localparam logic [7:0] LPAD = 8'h03;
    logic [7:0] command; 
    logic [23:0] data;
    logic [23:0] label;

    assign command = packet[31:24];
    assign data = packet[23:0];

    State next_state;

    always_comb begin
        next_state = state;

        case (state)
            IDLE: begin
                if (command == JUMP) begin
                    next_state = CHECK;
                end
            end
            CHECK: begin
                if ((command == LPAD) && (data == label)) begin
                    next_state = IDLE;
                end else begin
                    next_state = ERROR;
                end
            end
            ERROR: begin
                next_state = ERROR;
            end
            default: begin
                next_state = ERROR;
            end
        endcase
    end

    always_ff @(posedge clk) begin
        if (reset) begin
            state <= IDLE;
            label <= 24'd0;
        end else begin
            state <= next_state;
            if ((state == IDLE) && (command == SET)) begin
                label <= data;
            end
        end
    end
endmodule
