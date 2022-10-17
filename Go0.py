#!/usr/local/bin/python3
# /usr/bin/python3
# Set the path to your python3 above

#!/usr/bin/python3
# Set the path to your python3 above



from gtp_connection import GtpConnection
from board_base import DEFAULT_SIZE, GO_POINT, GO_COLOR
from board import GoBoard
from board_util import GoBoardUtil
from engine import GoEngine
from transposition_table import TT
import signal
from sys import platform
import time


class Go0:
    def __init__(self):
        """
        Go player that selects moves randomly from the set of legal moves.
        Does not use the fill-eye filter.
        Passes only if there is no other legal move.

        Parameters
        ----------
        name : str
            name of the player (used by the GTP interface).
        version : float
            version number (used by the GTP interface).
        """
        if platform!="win32":
            signal.signal(signal.SIGALRM, self.timeout_handler)
        self.timer=time.process_time()
        GoEngine.__init__(self, "Go0", 1.0)

    def timeout_handler(self,signum,frame):
        raise TimeoutError()


    def timeout_check(self):
        if time.process_time()-self.timer>self.timelimit:
            return True
        return False


    def start_timer(self):
        self.timer = time.process_time()


    def solver_negamax(self, board: GoBoard) -> int:
        legal=GoBoardUtil.generate_legal_moves(board, board.current_player)
        tt=TT()
        for m in legal:
            # nboard=board.copy()
            # nboard.play_move(m, nboard.current_player)
            board.play_legal(m,board.current_player)
            value=self.negamax(board,tt)
            board.undo(m,board.current_player)
            if value == False:
                return m
        return 0

    def negamax(self, board: GoBoard,tt) -> int:
        if platform=="win32":
            if self.timeout_check():
                raise TimeoutError()
        lookup = tt.lookup(board.code())
        if lookup:
            return lookup
        legal=GoBoardUtil.generate_legal_moves(board, board.current_player)
        if len(legal)==0:
            return False
        for m in legal:
            # nboard=board.copy()
            # nboard.play_move(m, board.current_player)
            # value = - self.negamax(nboard,tt)
            board.play_legal(m,board.current_player)
            value=not self.negamax(board,tt)
            board.undo(m,board.current_player)
            if value == True:
                tt.store(board.code(),True)
                return True
        tt.store(board.code(),False)
        return False

    def get_move(self, board: GoBoard, color: GO_COLOR) -> GO_POINT:
        try:
            if platform!="win32":
                signal.alarm(self.timelimit)
            else:
                self.start_timer()
            nboard=board.copy()
            move=self.solver_negamax(nboard)
            if platform!="win32":
                signal.alarm(0)
        except TimeoutError:
            return None
        return move

    
  
def run() -> None:
    """
    start the gtp connection and wait for commands.
    """
    board: GoBoard = GoBoard(DEFAULT_SIZE)
    con: GtpConnection = GtpConnection(Go0(), board)
    con.start_connection()


if __name__ == "__main__":
    run()
