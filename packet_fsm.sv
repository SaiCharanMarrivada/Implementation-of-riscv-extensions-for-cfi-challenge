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

    always_ff @(posedge clk) begin
        if (reset) begin
            state <= IDLE;
            label <= 24'd0;
        end else begin
            case (state)
                IDLE: begin
                    if (command == JUMP) begin
                        state <= CHECK;
                    end else if (command == SET) begin
                        state <= IDLE;
                        label <= data;
                    end
                end
                CHECK: begin
                    if ((command == LPAD) && (data == label)) begin
                        state <= IDLE;
                    end else begin
                        state <= ERROR;
                    end
                end
                ERROR: begin
                    state <= ERROR;
                end
                default: begin
                    state <= ERROR;
                end
            endcase
        end
    end
endmodule
